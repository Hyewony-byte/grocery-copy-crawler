import asyncio
import json
import requests
from playwright.async_api import async_playwright

# ⚠️ 본인의 구글 Apps Script 웹앱 배포 URL로 변경해 주세요
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwyw34cn3o8Kz1GuWjash1SaM_T1Tt2NT8wMF4BiIQ5tF72ZJlfPTwJ9Dn50oP70XrMDg/exec"

async def scrape_competitors():
    collected_data = []

    # [테스트용 강제 데이터] - 이 데이터가 시트에 들어오는지 먼저 확인!
    collected_data.append({
        "brand": "CJ더마켓",
        "section": "메인 배너 (Big Carousel)",
        "mainCopy": "자동 수집 테스트 카피입니다",
        "subCopy": "무료배송 혜택 확인하기 >",
        "category": "테스트/시즌"
    })

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # CJ더마켓
        try:
            print("--- CJ더마켓 수집 중 ---")
            await page.goto("https://www.cjthemarket.com/pc/main", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            banners = await page.locator(".banner_title, .main_title, h2, h3").all_inner_texts()
            for copy in banners[:5]:
                clean = copy.strip().replace("\n", " ")
                if len(clean) > 2:
                    collected_data.append({
                        "brand": "CJ더마켓",
                        "section": "메인 배너 (Big Carousel)",
                        "mainCopy": clean,
                        "subCopy": "공식몰 특가",
                        "category": "시즌/혜택"
                    })
        except Exception as e:
            print(f"CJ더마켓 수집 오류: {e}")

        # 컬리
        try:
            print("--- 컬리 수집 중 ---")
            await page.goto("https://www.kurly.com/main", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            titles = await page.locator("h2, span.title").all_inner_texts()
            for copy in titles[:5]:
                clean = copy.strip().replace("\n", " ")
                if len(clean) > 2:
                    collected_data.append({
                        "brand": "컬리",
                        "section": "영역 타이틀 (Section Title)",
                        "mainCopy": clean,
                        "subCopy": "주말 한정 혜택",
                        "category": "신선/초신선"
                    })
        except Exception as e:
            print(f"컬리 수집 오류: {e}")

        await browser.close()

    # Apps Script로 전송
    if collected_data:
        print(f"총 {len(collected_data)}건의 데이터를 구글 시트로 전송합니다.")
        try:
            res = requests.post(GAS_WEBHOOK_URL, json=collected_data, allow_redirects=True, timeout=15)
            print(f"구글 시트 전송 결과 (HTTP Status): {res.status_code}")
            print(f"구글 시트 응답 본문: {res.text}")
        except Exception as err:
            print(f"전송 예외 발생: {err}")

if __name__ == "__main__":
    asyncio.run(scrape_competitors())
