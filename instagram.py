import aiohttp

RAPID_API_KEY = "bcd1210fc7mshd7e3a940974a9b1p1338c1jsn2d121f0a43e1"

HEADERS = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "instagram120.p.rapidapi.com",
    "Content-Type": "application/json",
}

API_URL = "https://instagram120.p.rapidapi.com/api/instagram/posts"


async def get_instagram_video(instagram_url: str):
    payload = {
        "id": instagram_url
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL,
            headers=HEADERS,
            json=payload
        ) as response:

            if response.status != 200:
                return None

            data = await response.json()

            try:
                edges = data["result"]["edges"]

                for item in edges:
                    if not isinstance(item, dict):
                        continue

                    node = item.get("node")
                    if not node:
                        continue

                    videos = node.get("video_versions")
                    if videos:
                        return videos[0]["url"]

                return None

            except Exception:
                return None
