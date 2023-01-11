# 0. 코드 설명.
- [ERR]  : 에러
- [WARN] : 경고
- [INFO] : 정보

- J   : Json 파일 관련 코드
- K   : Key 관련 코드
    - e.g.) ERR.K.A -> API 키 관련 에러
    -  WARN.K.Dic -> 딕셔너리 키 관련 경고
- A   : API 관련 코드
- D   : 데이터 관련 코드
- Dic : 딕셔너리 관련 코드

# 1. JSON 관련 로그
- [ERR.J-0001] : 불러오고자 하는 JSON 파일이 경로상에 존재하지 않음.
    - [로그 위치 1] UTILS/utils.py -> SteamAPI 클래스 -> get_info 함수

- [ERR.K.A-0001] : API key를 저장하고 있는 원본, 백업 JSON 파일이 깨져 복구 필요.
    - [로그 위치 1] UTILS/utils.py -> repair_keys 함수


- [WARN.K.A-0001] : API key를 저장하고 있는 원본 JSON파일이 경로에 존재하지 않거나, 깨져 백업 파일로 사용.
    - [로그 위치 1] UTILS/utils.py -> get_key 함수



# 2. 데이터 관련 로그
- [WARN.D.A-0001] : steam API에서 전체 appid 목록을 조회했을때는 나오지만, 디테일한 정보를 얻을 때는 존재하지 않는 데이터
    - [로그 위치 1] UTILS/utils.py -> SteamAPI 클래스 -> most_played 함수
    - [로그 위치 2] UTILS/utils.py -> SteamAPI 클래스 -> get_stats 함수
    - [로그 위치 3] UTILS/utils.py -> SteamAPI 클래스 -> top_sellers 함수

- [WARN.D-0001] : 중복된 데이터 일 때
    - [로그 위치 1] UTILS.utils.py -> SteamAPI 클래스 -> top_sellers 함수