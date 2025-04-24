import os
import sys
from pathlib import Path


def setup_directories():
    """
    기본 디렉토리 구조를 생성하는 함수
    """
    # 프로젝트 루트 디렉토리 설정
    BASE_DIR = Path(__file__).resolve().parent

    # 필요한 디렉토리 목록
    directories = [
        BASE_DIR / "media",
        BASE_DIR / "media" / "courses",
        BASE_DIR / "static",
        BASE_DIR / "static" / "images",
        BASE_DIR / "static" / "css",
        BASE_DIR / "static" / "js",
    ]

    # 각 디렉토리가 존재하지 않으면 생성
    for directory in directories:
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✅ 디렉토리 생성 완료: {directory}")
            except Exception as e:
                print(f"❌ 디렉토리 생성 실패: {directory} - {e}")

    # 기본 정적 파일 생성
    create_default_files(BASE_DIR)

    print("\n모든 디렉토리 생성이 완료되었습니다.")
    print("이제 다음 명령으로 더미 데이터를 생성할 수 있습니다:")
    print("python manage.py seed_data --clear")


def create_default_files(base_dir):
    """
    기본 정적 파일 생성 함수
    """
    # 기본 이미지 파일
    default_image_path = base_dir / "static" / "images" / "default.jpg"
    if not default_image_path.exists():
        try:
            # 빈 이미지 파일 생성 (PIL을 사용할 수도 있지만, 간단한 방법으로 생성)
            with open(default_image_path, "wb") as f:
                # 8x8 투명 PNG 파일 (최소 크기)
                f.write(
                    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08\x00\x00\x00\x08\x08\x06\x00\x00\x00\xc4\x0f\xbe\x8b\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x0cIDAT\x18Wc\xf8\xff\xff?\x00\x05\x00\x01\x7f\xf2g\xc4\x00\x00\x00\x00IEND\xaeB`\x82"
                )
            print(f"✅ 기본 이미지 파일 생성 완료: {default_image_path}")
        except Exception as e:
            print(f"❌ 기본 이미지 파일 생성 실패: {e}")

    # 기본 CSS 파일
    default_css_path = base_dir / "static" / "css" / "default.css"
    if not default_css_path.exists():
        try:
            with open(default_css_path, "w") as f:
                f.write("/* 기본 CSS 파일 */")
            print(f"✅ 기본 CSS 파일 생성 완료: {default_css_path}")
        except Exception as e:
            print(f"❌ 기본 CSS 파일 생성 실패: {e}")


if __name__ == "__main__":
    setup_directories()
