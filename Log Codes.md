# 0. 코드 설명.
---

| 코드 | 설명 |
|:--:|:--|
|<span style="color: red">[ERR]</span>| 에러 |
|<span style="color: yellow">[WARN]</span>| 경고 |
|<span style="color: blue">[INFO]</span>| 정보 |

| 코드 | 설명 |
|:--:|:--|
|A| API 관련 코드|
|Co| 조건 관련 코드|
|D| 데이터 관련 코드|
|DB| DB 관련 코드|
|Dic| 딕셔너리 관련 코드|
|H| HTML 관련 코드|
|J| Json 파일 관련 코드|
|K| Key 관련 코드|
|Q| 쿼리 관련 코드|
|R| HTTP 상태 관련 코드|
|Red| Redis 관련 코드 |

- e.g.)
- <span style="color: red">[ERR.K.A]</span> -> API 키 관련 에러
- <span style="color: yellow">[WARN.K.Dic]</span> -> 딕셔너리 키 관련 경고
- <span style="color: blue">[INFO.DB.Red]</span> -> Redis DB 관련 정보 


# 1. 관련 로그
## 1-1. JSON 관련 로그
---
- <span style="color: red">[ERR.J-0001] : 불러오고자 하는 JSON 파일이 경로상에 존재하지 않음.</span>
    - [로그 위치 1] UTILS/utils.py -> SteamAPI 클래스 -> get_info 함수

- <span style="color: red">[ERR.K.A-0001] : API key를 저장하고 있는 원본, 백업 JSON 파일이 깨져 복구 필요.</span>
    - [로그 위치 1] UTILS/utils.py -> repair_keys 함수


- <span style="color: yellow">[WARN.K.A-0001] : API key를 저장하고 있는 원본 JSON파일이 경로에 존재하지 않거나, 깨져 백업 파일로 사용.</span>  
    - [로그 위치 1] UTILS/utils.py -> get_key 함수

## 1-2. 데이터 관련 로그
---
- <span style="color: yellow">[WARN.D-0001] : 중복된 데이터 일 때</span>
    - [로그 위치 1] UTILS.utils.py -> SteamAPI 클래스 -> get_topsellers 함수


- <span style="color: yellow">[WARN.D.A-0001] : steam API에서 전체 appid 목록을 조회했을때는 나오지만, 디테일한 정보를 얻을 때는 존재하지 않는 데이터</span>
    - [로그 위치 1] UTILS/utils.py  -> SteamAPI 클래스 -> most_played 함수
    - [로그 위치 2] UTILS/utils.py  -> SteamAPI 클래스 -> get_stats 함수
    - [로그 위치 3] UTILS/utils.py  -> SteamAPI 클래스 -> get_genre 함수
    - [로그 위치 3] gamedb/views.py -> gamedb 함수

- <span style="color: red">[ERR.D.H.0001] : HTML 태그에서 원하는 데이터를 찾을 수 없을 때 발생</span>
    - [로그 위치 1] UTILS/utils.py -> SteamAPI 클래스 -> get_trendy 함수



## 1-3. DB 관련 로그
---
- <span style="color: red">[ERR.DB.Q-0001] 쿼리에 이상이 있는 경우</span>
    - [로그 위치 1] UTILS/utils.py -> SalesDB 클래스 -> search_table 함수

- <span style="color: red">[ERR.DB.Co-0001] 인자값으로 들어간 정렬 기준이 조회할 column에 존재하지 않는 경우 발생</span>
    - e.g) 정렬 기준 : percent, 조회할 column : ['appid', 'original'] -> [ERR.DB.Co-0001] 발생
    - [로그 위치 1] UTILS/utils.py -> SalesDB 클래스 -> search_table 함수

- <span style="color: red">[ERR.DB.Co-0002] 인자 값으로 받은 비교 연산자가 미리 지정해둔 연산자에 없는 경우 발생</span>
    - e.g) 비교 연산자 : 'OUT', 미리 지정해둔 연산자 : ['>', '<', '!=', '=', '>=', '<=', 'IN'] -> [ERR.DB.Co-0002] 발생
    - [로그 위치 1] UTILS/utils.py -> SalesDB 클래스 -> search_table 함수


## 1-4. HTTP 통신 관련 로그
---
- <span style="color: red">[ERR.R-0001] HTML 통신 반환 내용이 200이 아닌 경우 발생</span>
    - [로그 위치 1] UTILS/utils.py -> return_or_print 함수
    - [로그 위치 2] UTILS/utils.py -> SteamAPI 클래스 -> get_trendy 함수