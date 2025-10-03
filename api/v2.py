import os
import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict
from operator import attrgetter

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi_problem.error import NotFoundProblem
from fastapi_problem.handler import add_exception_handler, new_exception_handler
from logbook import Logger
from unidecode import unidecode
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, Province, ProvinceCode, Ward, WardCode

from . import __version__
from .schema_v2 import ProvinceResponse, WardResponse


api_v2 = FastAPI(title='Vietnam Provinces online API (2025)', version=__version__)
eh = new_exception_handler()
add_exception_handler(api_v2, eh)
logger = Logger(__name__)


class ProvinceNotExistError(NotFoundProblem):
    title = 'Province not exist'


class WardNotExistError(NotFoundProblem):
    title = 'Ward not exist'


@api_v2.get('/', response_model=tuple[ProvinceResponse, ...])
def show_all_divisions(request: Request, depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions')):
    client_ip = request.client.host if request.client else None
    if depth > 1:
        env_value = os.getenv('BLACKLISTED_CLIENTS', '')
        blacklist = filter(None, (s.strip() for s in env_value.split(',')))
        if not client_ip or client_ip in blacklist:
            raise HTTPException(429)
    if depth >= 2:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    return tuple(asdict(p) for p in sorted(Province.iter_all(), key=attrgetter('code')))


@api_v2.get('/p/')
async def list_provinces(search: str = '') -> tuple[ProvinceResponse, ...]:
    provinces = sorted(Province.iter_all(), key=attrgetter('code'))
    keywords = search.strip().lower().split()
    if keywords:
        logger.info('To filter by {}', keywords)
        provinces = filter_provinces_by_keywords(provinces, keywords)
    return tuple(ProvinceResponse(**asdict(p)) for p in provinces)


@api_v2.get('/p/{code}')
def get_province(
    code: int,
    depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions', description='2: show wards'),
) -> ProvinceResponse:
    try:
        pcode = ProvinceCode(code)
    except ValueError as e:
        raise ProvinceNotExistError(f'No province has code {code}') from e
    response = asdict(Province.from_code(pcode))
    if depth >= 2:
        wards = sorted(Ward.iter_by_province(pcode), key=attrgetter('code'))
        response['wards'] = tuple(w for w in wards)
    return ProvinceResponse(**response)


@api_v2.get('/w/', response_model=None)
async def list_wards(
    request: Request, province: int = 0, search: str = ''
) -> tuple[WardResponse, ...] | RedirectResponse:
    if province:
        try:
            province_code = ProvinceCode(province)
        except ValueError:
            # For invalid province code, redirect to new URL this this parameter stripped
            url = request.url.remove_query_params('province')
            logger.info('Redirect to {}', url)
            return RedirectResponse(url)
        wards = Ward.iter_by_province(province_code)
    else:
        wards = Ward.iter_all()
    keywords = search.strip().lower().split()
    if keywords:
        logger.info('To filter by {}', keywords)
        # At this step, `wards` is an iterator, so when passing to filter_wards_by_keywords,
        # we need to convert it to a sequence, to allow iterating over it many times.
        wards = filter_wards_by_keywords(tuple(wards), keywords)
    return tuple(WardResponse(**asdict(p)) for p in sorted(wards, key=attrgetter('code')))


@api_v2.get('/w/{code}')
def get_ward(code: int) -> WardResponse:
    try:
        wcode = WardCode(code)
    except ValueError as e:
        raise WardNotExistError(f'No ward has code {code}') from e
    return WardResponse(**asdict(Ward.from_code(wcode)))


@api_v2.get('/search/provinces')
async def search_provinces(
    q: str = Query(..., min_length=1, description='Search query for province names'),
    limit: int = Query(10, ge=1, le=50, description='Maximum number of results to return')
) -> tuple[ProvinceResponse, ...]:
    """Search provinces by name with fuzzy matching support."""
    provinces = sorted(Province.iter_all(), key=attrgetter('code'))
    keywords = q.strip().lower().split()
    
    if keywords:
        logger.info('Searching provinces by keywords: {}', keywords)
        provinces = filter_provinces_by_keywords(provinces, keywords)
    
    # Limit results
    limited_provinces = list(provinces)[:limit]
    return tuple(ProvinceResponse(**asdict(p)) for p in limited_provinces)


@api_v2.get('/search/wards')
async def search_wards(
    q: str = Query(..., min_length=1, description='Search query for ward names'),
    province: int = Query(0, description='Filter by province code (0 for all provinces)'),
    limit: int = Query(20, ge=1, le=100, description='Maximum number of results to return')
) -> tuple[WardResponse, ...]:
    """Search wards by name with optional province filtering."""
    # Get wards based on province filter
    if province:
        try:
            province_code = ProvinceCode(province)
            wards = Ward.iter_by_province(province_code)
        except ValueError:
            raise HTTPException(400, detail=f'Invalid province code: {province}')
    else:
        wards = Ward.iter_all()
    
    # Convert to tuple for multiple iterations
    wards_list = tuple(wards)
    
    # Filter by search keywords
    keywords = q.strip().lower().split()
    if keywords:
        logger.info('Searching wards by keywords: {} (province: {})', keywords, province or 'all')
        filtered_wards = filter_wards_by_keywords(wards_list, keywords)
    else:
        filtered_wards = wards_list
    
    # Limit results
    limited_wards = list(filtered_wards)[:limit]
    return tuple(WardResponse(**asdict(w)) for w in limited_wards)


@api_v2.get('/search/all')
async def search_all(
    q: str = Query(..., min_length=1, description='Search query for provinces and wards'),
    limit: int = Query(15, ge=1, le=50, description='Maximum number of results per type')
) -> dict[str, tuple[ProvinceResponse | WardResponse, ...]]:
    """Search both provinces and wards simultaneously."""
    keywords = q.strip().lower().split()
    logger.info('Searching all divisions by keywords: {}', keywords)
    
    # Search provinces
    provinces = sorted(Province.iter_all(), key=attrgetter('code'))
    filtered_provinces = filter_provinces_by_keywords(provinces, keywords)
    limited_provinces = list(filtered_provinces)[:limit]
    
    # Search wards
    wards = tuple(Ward.iter_all())
    filtered_wards = filter_wards_by_keywords(wards, keywords)
    limited_wards = list(filtered_wards)[:limit]
    
    return {
        'provinces': tuple(ProvinceResponse(**asdict(p)) for p in limited_provinces),
        'wards': tuple(WardResponse(**asdict(w)) for w in limited_wards)
    }


def filter_provinces_by_keywords(provinces: Sequence[Province], keywords: Iterable[str]):
    # Mapping of province code -> unaccent province
    unaccent_province_mapping = {p.code: unidecode(p.name).lower() for p in provinces}
    unaccent_keywords = tuple(unidecode(w) for w in keywords)

    def is_name_matched(province: Province):
        name = unaccent_province_mapping[province.code]
        return all(word in name for word in unaccent_keywords)

    return filter(is_name_matched, provinces)


def filter_wards_by_keywords(wards: Sequence[Ward], keywords: Iterable[str]) -> Iterator[Ward]:
    # Mapping of ward code -> unaccent name
    unaccent_ward_mapping = {w.code: unidecode(w.name).lower() for w in wards}
    unaccent_keywords = tuple(unidecode(w) for w in keywords)

    def is_name_matched(ward: Ward):
        name = unaccent_ward_mapping[ward.code]
        return all(word in name for word in unaccent_keywords)

    return filter(is_name_matched, wards)


@api_v2.get('/parse-address')
async def parse_address(address: str = Query(..., description='Full address string to parse (2-level structure)')):
    """
    Parse Vietnamese address string into structured components (Province -> Ward only).
    
    API v2 uses 2-level structure: Province and Ward (no District level).
    
    Example inputs:
    - "456 haha, Xã Quang Trọng, Tỉnh Cao Bằng"
    - "Tỉnh Cao Bằng"
    - "Xã Quang Trọng, Cao Bằng"
    
    Returns structured address with codes for province, ward and street.
    """
    logger.info('Parsing address (v2): {}', address)
    
    # Split by comma and clean up
    parts = [p.strip() for p in address.split(',')]
    
    result = {
        'province': None,
        'province_code': None,
        'ward': None,
        'ward_code': None,
        'street': None
    }
    
    # Find province (usually last or mentioned with "Tỉnh/Thành phố")
    province_found = None
    for part in reversed(parts):
        for province in Province.iter_all():
            # Check if province name matches (with or without prefix)
            part_normalized = unidecode(part.lower())
            province_normalized = unidecode(province.name.lower())
            
            # Remove common prefixes for matching
            part_clean = re.sub(r'^(tinh|thanh pho|tp\.?)\s+', '', part_normalized)
            province_clean = re.sub(r'^(tinh|thanh pho|tp\.?)\s+', '', province_normalized)
            
            if part_clean in province_clean or province_clean in part_clean:
                province_found = province
                result['province'] = province.name
                result['province_code'] = province.code
                break
        if province_found:
            break
    
    if not province_found:
        # Try partial matching
        for part in reversed(parts):
            part_normalized = unidecode(part.lower()).strip()
            for province in Province.iter_all():
                province_name_simple = unidecode(province.name.lower())
                # Check if significant part of province name is in the input
                if len(part_normalized) >= 3 and part_normalized in province_name_simple:
                    province_found = province
                    result['province'] = province.name
                    result['province_code'] = province.code
                    break
            if province_found:
                break
    
    # Find ward if province found
    if province_found:
        province_code = ProvinceCode(province_found.code)
        wards = list(Ward.iter_by_province(province_code))
        
        for part in parts:
            for ward in wards:
                part_normalized = unidecode(part.lower())
                ward_normalized = unidecode(ward.name.lower())
                
                # Remove common prefixes
                part_clean = re.sub(r'^(phuong|xa|thi tran|tt\.?)\s+', '', part_normalized)
                ward_clean = re.sub(r'^(phuong|xa|thi tran|tt\.?)\s+', '', ward_normalized)
                
                if part_clean in ward_clean or ward_clean in part_clean:
                    result['ward'] = ward.name
                    result['ward_code'] = ward.code
                    break
            if result['ward']:
                break
    
    # Extract street (first part that doesn't match any division)
    for part in parts:
        part_normalized = unidecode(part.lower())
        is_division = False
        
        # Check if this part matches any found division
        for key in ['province', 'ward']:
            if result[key] and part_normalized in unidecode(result[key].lower()):
                is_division = True
                break
        
        if not is_division and part.strip():
            # This might be street/building number
            result['street'] = part.strip()
            break
    
    return result
