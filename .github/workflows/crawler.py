import asyncio
import json
import requests
from playwright.async_api import async_playwright

# 구글 Apps Script 웹 앱 배포 URL (본인의 웹앱 URL로 교체하세요!)
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbw6_eKCVxUV65h_mk3Nb9fq5Nsd7B-4VOw7_0nHcpa-t6t2wzi66cyMYYXS0A_jt09E3g/exec"

async def scrape_competitors():
    collected_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. CJ더마켓 수집
        try:
            print("--- CJ더마켓 수집 시작 ---")
            await page.goto("https://www.cjthemarket.com/pc/main", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            banners = await page.locator(".banner_title, .main_title, h2, h3").all_inner_texts()
            for copy in banners[:5]:
                clean_copy = copy.strip().replace("\n", " ")
                if len(clean_copy) > 2:
                    collected_data.append({
                        "brand": "CJ더마켓",
                        "section": "메인 배너 (Big Carousel)",
                        "mainCopy": clean_copy,
                        "subCopy": "온라인 공식몰 특가",
                        "category": "시즌/혜택"
                    })
        except Exception as e:
            print(f"CJ더마켓 수집 오류: {e}")

        # 2. 컬리 수집
        try:
            print("--- 컬리 수집 시작 ---")
            await page.goto("https://www.kurly.com/main", timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            titles = await page.locator("h2, span.title").all_inner_texts()
            for copy in titles[:5]:
                clean_copy = copy.strip().replace("\n", " ")
                if len(clean_copy) > 2:
                    collected_data.append({
                        "brand": "컬리",
                        "section": "영역 타이틀 (Section Title)",
                        "mainCopy": clean_copy,
                        "subCopy": "주말 한정 혜택",
                        "category": "신선/초신선"
                    })
        except Exception as e:
            print(f"컬리 수집 오류: {e}")

        await browser.close()

    # 구글 시트(Apps Script Webhook)로 수집 데이터 전송
    if collected_data:
        print(f"총 {len(collected_data)}건의 데이터를 구글 시트로 전송합니다.")
        try:
            res = requests.post(GAS_WEBHOOK_URL, json=collected_data, allow_redirects=True, timeout=15)
            print(f"전송 결과 응답코드: {res.status_code}")
        except Exception as send_err:
            print(f"구글 시트 전송 중 오류: {send_err}")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    asyncio.run(scrape_competitors())
