## Identify the data that we get from each one of these requests and find out which one to keep for best of our purpose

## Note (2026-03-30)
- In this VS Code terminal, these POST calls often return `HTTP 417` via `curl` (server blocks non-browser clients).
- A working workaround is to fetch via a real browser context using Playwright:
  - Run: `.venv/bin/python udise_pipeline.py fetch`
  - Outputs are written under `udise_api_dumps/`.

## Findings (verified via Playwright dumps)
- Keep (core): request #3 (mapId=117, `state=all`) — state-wise outcome table (48 cols, 181 rows for year=22).
- Optional: request #1 (mapId=117, `state=national`) — national aggregate (48 cols, 5 rows).
- Drop as duplicates: #6 and #8 (mapId=113 == mapId=117, identical columns+rows); #5 duplicates #4; #7 duplicates #2.
- GET_DISTRICT:
  - `condition:""` returns all districts (works).
  - Filtering by state works as `where udise_state_code='32' order by district_name`.
  - Adding `and ac_year='22'` returned 0 rows in our tests, so avoid `ac_year` unless you re-validate.
1. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getTabularData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw '{"mapId":117,"dependencyValue":"{\"year\":\"22\",\"state\":\"national\",\"dist\":\"none\",\"block\":\"none\"}","isDependency":"","paramName":"civilian","paramValue":"","schemaName":"national","reportType":"T"}'
2. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getMasterData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw $'{"extensionCall":"GET_DISTRICT","condition":"where udise_state_code= \'all\' and ac_year =\'22\' order by district_name "}'

3. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getTabularData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw '{"mapId":"117","dependencyValue":"{\"year\":\"22\",\"state\":\"all\",\"dist\":\"none\",\"block\":\"none\"}","isDependency":"Y","paramName":"civilian","paramValue":"","schemaName":"national","reportType":"T"}'

4. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getMasterData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  --data-raw $'{"extensionCall":"GET_STATE","condition":" where year_id=\'22\' order by state_name"}'

5. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getMasterData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw $'{"extensionCall":"GET_STATE","condition":" where year_id=\'22\' order by state_name"}'

6. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getTabularData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw '{"mapId":113,"dependencyValue":"{\"year\":\"22\",\"state\":\"national\",\"dist\":\"none\",\"block\":\"none\"}","isDependency":"","paramName":"civilian","paramValue":"","schemaName":"national","reportType":"T"}'

7. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getMasterData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw $'{"extensionCall":"GET_DISTRICT","condition":"where udise_state_code= \'all\' and ac_year =\'22\' order by district_name "}'

8. 
curl 'https://dashboard.udiseplus.gov.in/BackEnd-master/api/report/getTabularData' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: text/plain; charset=utf-8' \
  -H 'Origin: https://dashboard.udiseplus.gov.in' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://dashboard.udiseplus.gov.in/udiseplus-archive/' \
  -H 'Cookie: JSESSIONID=5658092FFA67DF7FF5ED283D0D80FC69; cookieWorked=yes' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  --data-raw '{"mapId":"113","dependencyValue":"{\"year\":\"22\",\"state\":\"all\",\"dist\":\"none\",\"block\":\"none\"}","isDependency":"Y","paramName":"civilian","paramValue":"","schemaName":"national","reportType":"T"}'