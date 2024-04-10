import logging

logging.basicConfig(level=logging.INFO)

from swibots import *
from fns import bash, run_async
from requests_cache import install_cache
import requests
from urllib.parse import quote
from decouple import config
from bs4 import BeautifulSoup
from youtubesearchpython import CustomSearch, SearchMode, Video, VideoUploadDateFilter

install_cache("valor")


@run_async
def get(url):
    return requests.get(url).json()



def getEvents():
    data = BeautifulSoup(
        requests.get("https://www.vlr.gg/events").content,
        "html.parser",
        from_encoding="utf8",
    )
    tiles = []
    for page in data.find("div", "events-container-col").find_all("a", "wf-card"):
        img = page.find("div", "event-item-thumb").find("img")
        twi = page.find("div", "mod-dates").contents[0].strip()
        prizes = page.find("div", "mod-prize").contents[0]
        tiles.append(
            ListTile(
                title=page.find("div", "event-item-title").text.strip()[:28],
                description_extra=twi,
                thumb="https:" + img.get("src"),
                description="Ongoing | " + "Prize: " + prizes.strip(),
                callback_data=f"evr|{page.get('href')}",
            )
        )
    return tiles

BOT_TOKEN = config("BOT_TOKEN", default="")

app = Client(
    BOT_TOKEN,
    app_bar=AppBar(
        left_icon="https://img.icons8.com/?size=48&id=GjCK2f2wpZxt&format=png",
        title="VALORANT",
    ),
    is_app=True,
    home_callback="Home"
)
app.set_bot_commands([BotCommand("start", "Get start message", True)])


def GetBottomBar(selected="Home"):
    pages = {
        "Home": {
            "icon": "https://f004.backblazeb2.com/file/switch-bucket/a8ebf6cc-dae5-11ee-ba6a-d41b81d4a9f0.png",
            "selected": "https://f004.backblazeb2.com/file/switch-bucket/03ad65d3-db56-11ee-8882-d41b81d4a9f0.png",
            "dark": "https://f004.backblazeb2.com/file/switch-bucket/b465a669-dae8-11ee-a429-d41b81d4a9f0.png"
        },
        "Agents": {
            "icon": "https://f004.backblazeb2.com/file/switch-bucket/a38af2f2-dae5-11ee-8eb4-d41b81d4a9f0.png",
            "selected": "https://f004.backblazeb2.com/file/switch-bucket/000dd1cf-db56-11ee-8c71-d41b81d4a9f0.png",
            "dark": "https://f004.backblazeb2.com/file/switch-bucket/b1b61df9-dae8-11ee-b092-d41b81d4a9f0.png"
        },
        "Maps": {
            "icon": "https://f004.backblazeb2.com/file/switch-bucket/aafc19d0-dae5-11ee-b340-d41b81d4a9f0.png",
            "selected": "https://f004.backblazeb2.com/file/switch-bucket/067a4f76-db56-11ee-969a-d41b81d4a9f0.png",
            "dark": "https://f004.backblazeb2.com/file/switch-bucket/b684b12b-dae8-11ee-9edd-d41b81d4a9f0.png"
        },
        "Lineups": {
            "icon": "https://f004.backblazeb2.com/file/switch-bucket/8e09362c-db56-11ee-a16e-d41b81d4a9f0.png",
            "selected": "https://f004.backblazeb2.com/file/switch-bucket/874e10d8-db56-11ee-8258-d41b81d4a9f0.png",
            "dark": "https://f004.backblazeb2.com/file/switch-bucket/8b09003a-db56-11ee-8c0c-d41b81d4a9f0.png"
        },
        "News": {"icon": "https://f004.backblazeb2.com/file/switch-bucket/ad32f3bb-dae5-11ee-ac50-d41b81d4a9f0.png",
                 "selected": "https://f004.backblazeb2.com/file/switch-bucket/09b41c45-db56-11ee-880c-d41b81d4a9f0.png",
                 "dark": "https://f004.backblazeb2.com/file/switch-bucket/b896ecce-dae8-11ee-84f0-d41b81d4a9f0.png"},
    }
    if not pages.get(selected):
        selected = list(pages.keys())[0]
    tiles = []
    for page, data in pages.items():
        tiles.append(
            BottomBarTile(
                page,
                icon=data["icon"],
                selection_icon=data["selected"],
                selected=selected == page,
                callback_data=page,
            )
        )
    return BottomBar(
        tiles,  theme_color="#c41028"
    )  # , BottomBarType.TOPLINE


@app.on_command("start")
async def onMes(ctx: BotContext[CommandEvent]):
    await ctx.event.message.reply_text(
        f"Hi, Welcome to {ctx.user.name}!\n\nClick below button to open app!",
        inline_markup=InlineMarkup(
            [[InlineKeyboardButton("Open APP", callback_data="Home")]]
        ),
    )


@app.on_callback_query(regexp("Premier"))
async def lnbHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    url = requests.get("https://tracker.gg/valorant/premier").content
    sp = BeautifulSoup(url, "html.parser")
    for card in sp.find_all("div", "premier-card"):
        if title := card.find("h4", "trn-card__title"):
            comps.append(Text(title.text.strip(), TextSize.SMALL))
        tiles = []
        for box in card.find_all("a", "standing"):
            tiles.append(
                ListTile(
                    box.text.strip(),
                    callback_data=f"Leaderboard|{box.get('href')}",
                    thumb=box.find("img").get("src"),
                )
            )
        if tiles:
            comps.append(ListView(tiles, ListViewType.SMALL))
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar())
    )


@app.on_callback_query(regexp("Leaderboard"))
async def lnbHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    url = "/valorant/premier/standings?page=1"
    if "|" in ctx.event.callback_data:
        url = ctx.event.callback_data.split("|")[-1]
    data = requests.get("https://tracker.gg" + url).content
    soup = BeautifulSoup(data, "html.parser")
    items = soup.find_all("div", "st-content__item")
#    print(items)
    tiles = []
    TITLE = soup.find("h1", "trn-card__title")
    if TITLE:
        comps.append(Text(TITLE.text.strip(), TextSize.SMALL))
    for tile in items:
        arv = tile.find_all("div", "value")
#        print(arv)
        tiles.append(
            ListTile(
                title=tile.find("h3").text.strip(),
                thumb=tile.find("img").get("src"),
                description=f"Score: {arv[1].text.strip()}",
                description_extra=f"Wins: {arv[0].text.strip()}",
            )
        )
    if tiles:
        comps.append(ListView(tiles))
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar("Home")),
        #        new_page=True,
    )


@run_async
def getYTInfo(url):
    return Video.getInfo(url)
#    return YoutubeDL().extract_info(url, download=False)


@app.on_callback_query(regexp("ytplay"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    url = ctx.event.callback_data.split("|")[-1]
    output = await bash(f'yt-dlp -g -f "best[height<=?720][width<=?1280]" {url}')
    videoInfo = await getYTInfo(url)
#    print(videoInfo)
    comps = [VideoPlayer(output, title=videoInfo["title"], full_screen=True)]
    if ch := videoInfo.get("channel"):
        comps.append(Text(f"*Channel:* {ch['name']}"))
    if vw := videoInfo.get("viewCount"):
        comps.append(Text(f"*Views:* {vw['text']}"))
    if vw := videoInfo.get("description"):
        comps.append(Text(f"*Description:* {vw[:500]}"))
    await ctx.event.answer(callback=AppPage(components=comps))


@run_async
def getVideos(query, region="US"):
    response = CustomSearch(
        query, SearchMode.livestreams, region=region, limit=50
    ).result()["result"]
    response.extend(
        CustomSearch(
            query, VideoUploadDateFilter.lastHour, region=region, limit=30
        ).result()["result"]
    )
    return response


Flt = {}


@app.on_callback_query(regexp("Filters"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    user = ctx.event.action_by_id
    if not Flt.get(user):
        Flt[user] = {}
    if "|" in ctx.event.callback_data:
        spl = ctx.event.callback_data.split("|")[-1].split("+")
        Flt[user][spl[0]] = spl[1]
    cts = requests.get("https://restcountries.com/v3.1/all").json()
    agts = requests.get("https://valorant-api.com/v1/agents").json()
    comps.append(Text("Filters", TextSize.SMALL))
    comps.append(
        Dropdown(
            (
                f"Selected: {Flt[user]['loc']}"
                if Flt[user].get("loc")
                else "Select Country"
            ),
            options=sorted(
                [
                    ListItem(
                        til["name"]["common"],
                        callback_data=f"Filters|loc+{til['cca2']}",
                    )
                    for til in cts
                ],
                key=lambda x: x.title,
            ),
        )
    )
    comps.append(
        Dropdown(
            Flt[user].get("agr") or "Select Agent",
            options=[
                ListItem(
                    til["displayName"],
                    callback_data=f"Filters|agr+{til['displayName']}",
                )
                for til in agts["data"]
            ],
        )
    )
    comps.append(Button("Continue", callback_data="streams"))
    await ctx.event.answer(
        callback=AppPage(
            components=comps, bottom_bar=GetBottomBar("Home")
        )  # screen=ScreenType.BOTTOM,
    )


@app.on_callback_query(regexp("streams"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    info = Flt.get(ctx.event.action_by_id) or {}
#    print(info)
    res = await getVideos(("Valorant " + info.get("agr", "")).strip(), info.get("loc"))
    comps.append(Button("Set Filters", callback_data="Filters", color="#c41028"))
    if res:
        tiles = []
        for vid in res:
            tiles.append(
                ListTile(
                    title=vid["title"],
                    thumb=vid["thumbnails"][0]["url"],
                    description=vid["channel"]["name"],
                    callback_data=f"ytplay|{vid['link']}",
                    badges=[
                        Badge("Live", background="#c41028"),
                    ],
                )
            )
        comps.append(ListView(tiles, ListViewType.LARGE))
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar("Home"))
    )


from swibots.api.callback.Button import ButtonVariant


@app.on_callback_query(regexp("Home"))
async def onHome(ctx: BotContext[CallbackQueryEvent]):
    comps = [
        TextInput(
            placeholder="Enter username#id",
            callback_data="profile",
            label="Enter username",
        ),
        Button("Open Profile", callback_data="profile", color="#c41028"),
    ]
    data = BeautifulSoup(
        requests.get("https://tracker.gg/valorant").content,
        "html.parser",
        from_encoding="utf8",
    )
    comps.append(
        Button(
            Text(
            "Live Streams",
            color="#e05f55",
                )
           ,
            callback_data="streams",
            variant=ButtonVariant.OUTLINED,
            color="#c41028",
        )
    )
    if lead := data.find("div", "leaders"):
        tiles = []
        for card in lead.find_all("div", "leader-card"):
            atag = card.find("a", "avatar-container")
            spl = atag.get("href").split("/")
#            print(spl)
            tiles.append(
                GridItem(
                    media=card.find("img", "user-avatar__image").get("src"),
                    title=card.find("span", "trn-ign__username").text,
                    callback_data=f"profile|{spl[-1]}",
                )
            )
        comps.append(Grid(title="Top Leaders", options=tiles, horizontal=True))
    comps.append(
        Grid(
            title="More Options",
            options=[
                GridItem(
                    "Premier",
                    media="https://img.icons8.com/?size=64&id=Wm9BpxflIpY0&format=png",
                    callback_data="Premier",
                ),
                GridItem(
                    "Buddies",
                    media="https://img.icons8.com/?size=64&id=Wm9BpxflIpY0&format=png",
                    callback_data="Buddies",
                ),
                GridItem(
                    "Weapons",
                    media="https://img.icons8.com/?size=64&id=Wm9BpxflIpY0&format=png",
                    callback_data="Weapons",
                ),
                GridItem(
                    "Cards",
                    media="https://img.icons8.com/?size=64&id=Wm9BpxflIpY0&format=png",
                    callback_data="Cards",
                ),
                GridItem(
                    "Game Mode",
                    media="https://img.icons8.com/?size=64&id=Wm9BpxflIpY0&format=png",
                    callback_data="GameMode",
                ),
            ],
            horizontal=True,
            grid_type=GridType.SMALL,
        )
    )
    comps.append(Spacer(y=14))
    """
    episodes = BeautifulSoup(
        requests.get("https://valorant.fandom.com/wiki/Episodes").content,
        "html.parser",
        from_encoding="utf8",
    )
    if tba := episodes.find("table", "wikitable"):
        tiles = []
        for d in tba.find("tbody").find_all("tr"):
            if not d.find_all("td"):
                continue
            tiles.append(
                ListTile(
                    d.find("b").text.strip(),
                 thumb=d.find("img").get("src")   
                )
            )
        comps.append(
            ListView(
                tiles,
                view_type=ListViewType.COMPACT,
            )
        )
    """
    comps.append(Text("Ongoing Events", TextSize.SMALL))
    comps.append(
        ListView(
            options=getEvents()[:7],
            right_image="https://f004.backblazeb2.com/file/switch-bucket/9c99cba4-a988-11ee-8ef4-d41b81d4a9ef.png",
            image_callback="Events",
        )
    )
    comps.append(Button("View All", callback_data="Events", color="#c41028"))
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar("Home"))
    )


@app.on_callback_query(regexp("Buddies"))
async def __(ctx: BotContext[CallbackQueryEvent]):
    await GetPage(ctx, "Buddies")


@app.on_callback_query(regexp("Cards"))
async def __(ctx: BotContext[CallbackQueryEvent]):
    await GetPage(ctx, "Cards", "playercards")


@app.on_callback_query(regexp("Weapons"))
async def __(ctx: BotContext[CallbackQueryEvent]):
    await GetPage(ctx, "Weapons", "weapons")


@app.on_callback_query(regexp("GameMode"))
async def __(ctx: BotContext[CallbackQueryEvent]):
    await GetPage(ctx, "GameMode", "gamemodes")


@app.on_callback_query(regexp("Sprays"))
async def GetPage(
    ctx: BotContext[CallbackQueryEvent], clb="Sprays", key=None, expand=False
):
    comps = []
    page = 0
    offset = 48
    if "|" in ctx.event.callback_data:
        page = int(ctx.event.callback_data.split("|")[-1])
    data = requests.get(f"https://valorant-api.com/v1/{(key or clb).lower()}").json()[
        "data"
    ]
    total = len(data)
    #    print(page)
    current = data[page * offset :][:offset]
#    print(clb, current)
    if clb == "GameMode":
        comps.append(
            ListView(
                options=[
                    ListTile(
                        d["displayName"] or "",
                        thumb=d.get("fullTransparentIcon")
                        or d.get("fullIcon")
                        or d.get("largeIcon")
                        or d.get("displayIcon")
                        or "",
                        callback_data="",
                    )
                    for d in current
                    if d.get("displayIcon")
                ]
            )
        )
    else:
        comps.append(
            Grid(
                clb,
                options=[
                    GridItem(
                        d["displayName"] or "",
                        media=d.get("fullTransparentIcon")
                        or d.get("fullIcon")
                        or d.get("largeIcon")
                        or d.get("displayIcon")
                        or "",
                    )
                    for d in current
                ],
                #  size=4,
                grid_type=GridType.SMALL,
                expansion=Expansion.HORIZONTAL if expand else Expansion.DEFAULT,
            ),
        )
    bts = []
    if page > 0:
        bts.append(Button("<<", callback_data=f"{clb}|{page-1}", color="#c41028"))
    if (page * offset) + offset < total:
        bts.append(Button(">>", callback_data=f"{clb}|{page+1}", color="#c41028"))
    if bts:
        comps.append(ButtonGroup(bts))
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar(clb))
    )


@app.on_callback_query(regexp("Agents"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = [Text("Agents", TextSize.SMALL)]
    data = await get("https://valorant-api.com/v1/agents?isPlayableCharacter=true")
    rows = []
    for bdata in data["data"]:
#        print(bdata.get("role"))
        rows.append(
            ListTile(
                bdata["displayName"],
                description=bdata["description"][:58] + "...",
                subtitle=(bdata.get("role") or {}).get("displayName"),
                thumb=bdata["displayIcon"],
                callback_data=f"agt|{bdata['uuid']}",
            )
        )
    comps.append(ListView(rows, ListViewType.LARGE))
    await ctx.event.answer(
        callback=AppPage(
            components=comps, bottom_bar=GetBottomBar(ctx.event.callback_data)
        )
    )


@app.on_callback_query(regexp("profile"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    user = ctx.event.action_by_id
    if val := ctx.event.details.input_value:
        Conf[user] = val
        return
    query = quote(Conf.get(user, ""))
#    print(query)
    if "|" in ctx.event.callback_data:
        query = ctx.event.callback_data.split("|")[-1]
    if not query:
        await ctx.event.answer("Provide username of user!", show_alert=True)
        return
    #    query = ctx.event.callback_data.split("|")[-1]
    page = BeautifulSoup(
        requests.get(
            f"https://tracker.gg/valorant/profile/riot/{query}/overview"
        ).content,
        "html.parser",
    )
    comps = []
    if im := page.find("img", "object-cover"):
        comps.append(Image(im.get("src").split()[0]))
    comps.append(
        ListView(
            [
                ListTile(
                    title=page.find("span", "ph-details__name").text.strip(),
                    thumb=page.find("img", "user-avatar__image").get("src"),
                )
            ],
            view_type=ListViewType.LARGE,
        )
    )
    if wps := page.find("div", "area-top-weapons"):
        tiles = []
        for tile in wps.find_all("div", "weapon"):
            tiles.append(
                ListTile(
                    title=tile.find("div", "weapon__name").text.strip(),
                    thumb=tile.find("img").get("src"),
                    description="Kills: "
                    + tile.find("div", "weapon__main-stat")
                    .find("span", "value")
                    .text.strip(),
                )
            )
        comps.append(Text("Top Weapons", TextSize.SMALL))
        comps.append(ListView(tiles, ListViewType.LARGE))
    if wps := page.find("div", "area-top-maps"):
        tiles = []
        for tile in wps.find_all("div", "top-maps__maps-map"):
#            print(tile)
            tiles.append(
                ListTile(
                    title=tile.find("div", "name").text.strip(),
                    thumb=tile.get("style").split("'")[1].strip(),
                    description=tile.find("div", "info")
                    .find("div", "value")
                    .text.strip(),
                )
            )
        comps.append(Text("Top Maps", TextSize.SMALL))
        comps.append(ListView(tiles))
    await ctx.event.answer(callback=AppPage(components=comps))


Conf = {}


@app.on_callback_query(regexp("agt"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    query = ctx.event.callback_data.split("|")[-1]
    data = requests.get(f"https://valorant-api.com/v1/agents/{query}").json()["data"]
    comps = [
        #        Image(data["listViewIcon"]),
        Image(data["fullPortrait"]),
        Text(data["displayName"], TextSize.SMALL),
    ]
    if desc := data.get("description"):
        comps.append(Text(desc))
    cles = data["abilities"]
    for abs in cles:
        comps.append(
            Accordian(
                abs["displayName"],
                icon=abs["displayIcon"],
                components=[Image(abs["displayIcon"]), Text(abs["description"])],
            )
        )
    ext = BeautifulSoup(
        requests.get(
            f"https://valorant.fandom.com/wiki/{data['displayName']}?wikia-footer-wiki-rec=true"
        ).content,
        "html.parser",
    )
    if gallery := ext.find("div", id="gallery-1"):
        comps.append(
            Grid(
                title="Image Gallery",
                horizontal=True,
                expansion=Expansion.HORIZONTAL,
                options=[
                    GridItem("", media=img.get("data-src"))
                    for img in gallery.find_all("img")[::-1]
                    if img.get("data-src")
                ],
            )
        )
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar("Agents")),
        new_page=True,
    )


@app.on_callback_query(regexp("map"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    query = ctx.event.callback_data.split("|")[-1]
    data = requests.get(f"https://valorant-api.com/v1/maps/{query}").json()["data"]
    comps = [
        #        Image(data["listViewIcon"]),
        Image(data["splash"]),
        Text(data["displayName"], TextSize.SMALL),
    ]
    if desc := data.get("narrativeDescription"):
        comps.append(Text(desc))
    if desc := data.get("tacticalDescription"):
        comps.append(Text(desc))
    cles = data["callouts"]
    comps.append(Text("Places", TextSize.SMALL))
    #   while cles:
    comps.append(Text(" | ".join([t["regionName"] for t in cles][:10])))
    #    cles = cles[5:]
    await ctx.event.answer(
        callback=AppPage(components=comps, bottom_bar=GetBottomBar("Maps")),
        new_page=True,
    )


@app.on_callback_query(regexp("Maps"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = [Text("Maps", TextSize.SMALL)]
    data = await get("https://valorant-api.com/v1/maps")
    rows = []
    for bdata in data["data"]:
#        print(bdata)
        rows.append(
            ListTile(
                bdata["displayName"],
                description=(bdata.get("narrativeDescription") or "")[:58],
                thumb=bdata["splash"],
                callback_data=f"map|{bdata['uuid']}",
            )
        )
    comps.append(ListView(rows, ListViewType.COMPACT))
    await ctx.event.answer(
        callback=AppPage(
            components=comps, bottom_bar=GetBottomBar(ctx.event.callback_data)
        )
    )


@app.on_callback_query(regexp("evr"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    url = ctx.event.callback_data.split("|")[-1]
    data = BeautifulSoup(
        requests.get("https://www.vlr.gg" + url).content,
        "html.parser",
        from_encoding="utf8",
    )
    img = data.find("div", "wf-avatar")
    if img.find("img"):
        comps.append(Image("https:" + img.find("img").get("src")))
    title = data.find("h1", "wf-title")
    if title:
        comps.append(Text(title.text.strip(), TextSize.SMALL))
    cont = data.find("div", "event-teams-container")
    if cont:
        comps.append(
            Grid(
                title="Teams",
                options=[
                    GridItem("", media="https:" + d.find("img").get("src"))
                    for d in cont.find_all("div", "wf-card")
                ],
            )
        )
    await ctx.event.answer(callback=AppPage(components=comps), new_page=True)


@app.on_callback_query(regexp("news"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    url = "https://tracker.gg" + ctx.event.callback_data.split("|")[-1]
    content = BeautifulSoup(
        requests.get(url).content, "html.parser", from_encoding="utf8"
    )
    if h1 := content.find("h1"):
        comps.append(Text(h1.text.strip(), TextSize.SMALL))
    if h1 := content.find("h2"):
        comps.append(Text(h1.text.strip(), TextSize.SMALL))
    content = content.find("div", "article__content")
    if img := content.find("img"):
        comps.append(Image(img.get("src")))
    items = content.find("div", id="article-content")
    for p in items.children:
        if p.name == "p":
            comps.append(Text(p.text.strip()))
        elif p.name == "h2":
            comps.append(Text(p.text, TextSize.SMALL))
        elif p.name == "figure" and p.get("src"):
            comps.append(Image(p.get("src")))
        else:
            print(p, p.name)
    await ctx.event.answer(
        callback=AppPage(
            components=comps,
            bottom_bar=GetBottomBar("News"),
        ),
        #        new_page=True,
    )


@app.on_callback_query(regexp("vlineup"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    url = "https://tracker.gg" + ctx.event.callback_data.split("|")[-1]
    content = BeautifulSoup(
        requests.get(url).content, "html.parser", from_encoding="utf8"
    )
    url = content.find("iframe").get("src")
    newsoup = BeautifulSoup(
        requests.get(url).content, "html.parser", from_encoding="utf8"
    )
    stream = newsoup.find("stream")
    # https://customer-9h7e8ahl6hivmjb6.cloudflarestream.com/95145d16b0394c31b23eb35e46eec714/manifest/video.mpd?
    newUrl = f"https://{stream.get('customer-domain-prefix')}.cloudflarestream.com/{stream.get('src')}/manifest/video.mpd?"
    comps.append(
        VideoPlayer(
            newUrl,
            title=content.find("h1").text.strip(),
            full_screen=True,
        )
    )
    await ctx.event.answer(
        callback=AppPage(
            components=comps,
            bottom_bar=GetBottomBar("Lineups"),
        ),
        new_page=True,
    )


@app.on_callback_query(regexp("News"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    content = BeautifulSoup(
        requests.get("https://tracker.gg/valorant/premier/news").content, "html.parser"
    )
    comps = []
    tiles = []
    for key in ["article-tile", "article-list-item"]:
        for new in content.find_all("div", key):
            atag = new.find("a", "article-list-item__title") or new.find(
                "a", "article-tile__title"
            )
            tiles.append(
                ListTile(
                    title=atag.text.strip(),
                    thumb=new.find("img").get("src"),
                    callback_data=f"news|{atag.get('href')}",
                )
            )
    if tiles:
        comps.append(
            ListView(title="News", options=tiles, view_type=ListViewType.LARGE)
        )

    await ctx.event.answer(
        callback=AppPage(
            components=comps, bottom_bar=GetBottomBar(ctx.event.callback_data)
        )
    )


@app.on_callback_query(regexp("Lineups"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = []
    agent = "all agents"
    if "|" in ctx.event.callback_data:
        agent = ctx.event.callback_data.split("|")[-1]
    url = "https://tracker.gg/valorant/guides/clips" + (
        "?agent=" + agent if agent and agent != "all agents" else ""
    )
#    print(url)
    soup = BeautifulSoup(
        requests.get(url).content,
        "html.parser",
        from_encoding="utf8",
    )

    lines = [
        TabBarTile(
            t.text,
            callback_data=f"Lineups|{t.text.lower()}",
            selected=t.text.lower() == agent,
        )
        for t in soup.find("div", "filter")
        .find("ul", "dropdown__items")
        .find_all("li", "dropdown__item")
    ]
    comps.append(TabBar(lines))
    rows = []
    mainV = soup.find("div", "guides__list")
    for tile in mainV.find_all("div", "guide-tile"):
        title = tile.find("p", "guide-tile__title")
        rows.append(
            ListTile(
                title.text.strip(),
                description=  # "👀 "
                # + tile.find("span", "views").text.strip()
                " | " + tile.find("span", "guide-tile__timestamp").text.strip(),
                thumb=tile.find("div", "guide-tile__video").find("img").get("src"),
                callback_data=f"vlineup|{title.find('a').get('href')}",
                badges=[
                    Badge(span.text)
                    for span in tile.find("div", "guide-tile__badges").find_all("span")
                ],
            )
        )
    comps.append(
        ListView(rows, title="LineUps", view_type=ListViewType.COMPACT)
    )  # ListViewType.COMPACT,
    await ctx.event.answer(
        callback=AppPage(
            components=comps, bottom_bar=GetBottomBar(ctx.event.callback_data)
        )
    )


@app.on_callback_query(regexp("Events"))
async def SampleHome(ctx: BotContext[CallbackQueryEvent]):
    comps = [Text("Events", TextSize.SMALL), ListView(options=getEvents())]
    await ctx.event.answer(
        callback=AppPage(
            components=comps, bottom_bar=GetBottomBar(ctx.event.callback_data)
        )
    )

app.run()
