import asyncio
import json
import requests
from playwright.async_api import async_playwright

# 구글 Apps Script 웹 앱 URL (배포하신 웹앱 URL로 변경)
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbw6_eKCVxUV65h_mk3Nb9fq5Nsd7B-4VOw7_0nHcpa-t6t2wzi66cyMYYXS0A_jt09E3g/exec"

async def scrape_competitors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        collected_data = []

        # 1. CJ더마켓 수집
        try:
            print("CJ더마켓 수집 중...")
            await page.goto("https://www.cjthemarket.com/pc/main", timeout=30000)
            await page.wait_for_timeout(3000)
            
            banners = await page.locator(".banner_title, .main_title").all_inner_texts()
            for copy in banners[:3]:
                if copy.strip():
                    collected_data.append({
                        "brand": "CJ더마켓",
                        "section": "메인 배너 (Big Carousel)",
                        "mainCopy": copy.strip(),
                        "subCopy": "",
                        "category": "자동수집"
                    })
        except Exception as e:
            print(f"CJ더마켓 수집 오류: {e}")

        # 2. 컬리 수집
        try:
            print("컬리 수집 중...")
            await page.goto("https://www.kurly.com/main", timeout=30000)
            await page.wait_for_timeout(3000)
            
            titles = await page.locator("h2").all_inner_texts()
            for copy in titles[:3]:
                if copy.strip():
                    collected_data.append({
                        "brand": "컬리",
                        "section": "영역 타이틀 (Section Title)",
                        "mainCopy": copy.strip(),
                        "subCopy": "",
                        "category": "자동수집"
                    })
        except Exception as e:
            print(f"컬리 수집 오류: {e}")

        await browser.close()

        # 구글 시트(Apps Script)로 데이터 전송
        if collected_data:
            print(f"총 {len(collected_data)}건의 데이터를 구글 시트로 전송합니다.")
            requests.post(GAS_WEBHOOK_URL, json=collected_data)

asyncio.run(scrape_competitors())
