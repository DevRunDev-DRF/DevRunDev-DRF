## 소셜 로그인 설정

### Google OAuth 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트 생성
2. OAuth 2.0 클라이언트 ID 생성
   - 승인된 리디렉션 URI: `http://localhost:8000/accounts/google/login/callback/`
3. 발급받은 클라이언트 ID와 시크릿을 `.env`에 설정
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
### Kakao OAuth 설정
1. [Kakap Developers](https://developers.kakao.com/)에서 애플리케이션 추가
2. 카카오 로그인 활성화 및 Redirect URI 설정, 동의 항목 설정
   - Redirect URI: `http://localhost:8000/accounts/kakao/login/callback/`, `http://localhost:8000/oauth`
3. 발급받은 REST API 키를 `.env`에 설정
   ```
   KAKAO_CLIENT_ID=Your REST API KEY
   KAKAO_CLIENT_SECRET= 'None'
   ```

### Naver OAuth 설정
1. [Naver Developers](https://developers.naver.com/products/login/api/api.md)에서 오픈 API 이용 신청
2. 사용 API를 네이버 로그인으로 설정 및 제공 정보 설정
3. 로그인 오픈 API 서비스 환경 설정
   - 서비스 URL : `http://localhost:8000/`
   - 네이버 로그인 Callback URL : `http://localhost:8000/accounts/naver/login/callback/`
4. 발급받은 클라이언트 ID와 시크릿을 `.env`에 설정
   ```
   Naver_CLIENT_ID=your-client-id
   Naver_CLIENT_SECRET=your-client-secret
   ```