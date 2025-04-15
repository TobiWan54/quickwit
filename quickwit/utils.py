"""Contains utility methods used throughout the package"""
from logging import getLogger
from typing import Callable, TypeVar, Coroutine, Sequence
from datetime import datetime
import pytz
import discord


T = TypeVar('T')

EVENT_ROLE_NAME = 'Events'

EMOJIS = [
    ('Tank', '<:Tank:1361715148275978281>'),
    ('Healer', '<:Healer:1361714958634713200>'),
    ('DPS', '<:DPS:1361714957619564737>'),
    ('CampfireEvent','<:Campfire:1361719739092828160>'),
    ('FashionShow','<:FashionShow:1361719741852422174>'),
    ('Judge','<:Judge:1361719743437996193>'),
    ('Speaker','<:Speaker:1361719746659356892>'),
    ('Crowd','<:Crowd:1361720304933539904>'),
    ('Model','<:Model:1361720306678366370>'),
    ('Duration','<:Duration:1361714964750143719>'),
    ('FinalFantasyXIV','<:FF14:1361715995215138837>'),
    ('Event','<:Event:1361722436982407218>'),
    ('Attending','<:Attending:1361714961918853240>'),
    ('Organiser','<:Organiser:1361714967279177748>'),
    ('People','<:People:1361714963483197500>'),
    ('Start','<:Start:1361714968822546583>'),
    ('Tentative','<:Tentative:1361714954537013391>'),
    ('Late','<:Late:1361723397637411036>'),
    ('Bench','<:Bench:1361714956445286450>'),
    ('Allrounder','<:Allrounder:1361714960648114347>'),
    ('Pictomancer','<:Pictomancer:1264644682646814883>'),
    ('BlueMage','<:BlueMage:1264644552975974551>'),
    ('Samurai','<:Samurai:1264645159795298497>'),
    ('Reaper','<:Reaper:1264645141373915220>'),
    ('Ninja','<:Ninja:1264645180099657769>'),
    ('Monk','<:Monk:1264645224160956492>'),
    ('Machinist','<:Machinist:1264645265713926206>'),
    ('Dragoon','<:Dragoon:1264645202195255296>'),
    ('Dancer','<:Dancer:1264645244469772369>'),
    ('Summoner','<:Summoner:1264645116279394416>'),
    ('RedMage','<:RedMage:1264644745666236536>'),
    ('BlackMage','<:BlackMage:1301689997300076606>'),
    ('Bard','<:Bard:1264645295564783666>'),
    ('WhiteMage','<:WhiteMage:1264644527935852635>'),
    ('Scholar','<:Scholar:1264644505965953126>'),
    ('Sage','<:Sage:1264644450542424085>'),
    ('Astrologian','<:Astrologian:1264644473116426291>'),
    ('Warrior','<:Warrior:1264644632541659219>'),
    ('Paladin','<:Paladin:1264644652061954218>'),
    ('GunBreaker','<:Gunbreaker:1264644584131268668>'),
    ('DarkKnight','<:DarkKnight:1264644608688914585>'),
    ('Viper', '<:Viper:1264644722937561221>')
]


async def grab_by_id(a_id: int, get_from_cache: Callable[[int], T],
                     fetch_from_api: Coroutine[None, int, T]) -> T | None:
    """Grabs a Discord resource by ID. First from cache, then from API calls

    Args:
        a_id (int): The ID of the item to grab
        get_from_cache (Callable[[int], T]): The method to get it from cache
        fetch_from_api (Coroutine[None, int, T]): The method to fetch it from API

    Returns:
        T | None: The The resource
    """
    result = get_from_cache(a_id)
    if result is None:
        try:
            getLogger(__name__).info(
                'Using %s to fetch resource with ID: %s', fetch_from_api.__name__, a_id)
            result = await fetch_from_api(a_id)
        except (discord.NotFound, discord.HTTPException) as e:
            getLogger(__name__).error(
                'Encountered error while fetching channel: %s', e)
            return None
    return result


def get_emoji_by_name(emojis: Sequence[discord.Emoji], name: str) -> str:
    """Find an emoji in a sequence by its name, returning a default emoji when not found

    Args:
        emojis (Sequence[discord.Emoji]): The sequence of emojis to search through
        name (str): The name of the emoji to find

    Returns:
        str: The emoji, rendered for Discord
    """
    for e in EMOJIS:
        if e[0].lower() == name.replace(' ', '').lower():
            return e[1]
    return '❓'


async def get_event_role(guild: discord.Guild) -> discord.Role:
    "Retrieves the Event role from a Guild, defaulting to guild's default role"
    if len(guild.roles) == 0:
        await guild.fetch_roles()

    for role in guild.roles:
        if role.name == EVENT_ROLE_NAME:
            return role
    return guild.default_role


def strptime_no_exception(datetime_str: str, format_str) -> datetime | None:
    """Executes datetime.strptime without throwing an exception"""
    try:
        return datetime.strptime(datetime_str, format_str)
    except ValueError:
        pass
    return None


def get_datetime_from_supported_formats(datetime_str: str) -> datetime:
    """Returns a datetime object parsed from any supported format

    Raises:
        ValueError: Raised when no supported pattern matches
    """
    dt = strptime_no_exception(datetime_str, '%d-%m-%Y %H:%M')
    now = datetime.now()
    if dt is None:
        dt = strptime_no_exception(datetime_str, '%d/%m/%Y %H:%M')
    if dt is None:
        dt = strptime_no_exception(datetime_str, '%d-%m %H:%M')
        if dt is not None:
            dt = dt.replace(year=now.year)
    if dt is None:
        dt = strptime_no_exception(datetime_str, '%d/%m %H:%M')
        if dt is not None:
            dt = dt.replace(year=now.year)
    if dt is None:
        dt = strptime_no_exception(datetime_str, '%H:%M')
        if dt is not None:
            dt = dt.replace(year=now.year, month=now.month, day=now.day)
    if dt is None:
        raise ValueError(
            f'Could not match {datetime_str} to any supported format')
    return dt


def get_timezone_aware_datetime_from_supported_formats(
        datetime_str: str,
        timezone: pytz.tzinfo.BaseTzInfo) -> datetime:
    """Generate a timezone aware datetime object from string

    Raises:
        ValueError: Raised when no supported pattern matches
    """
    dt = get_datetime_from_supported_formats(datetime_str)
    dt = timezone.localize(dt)
    return dt.astimezone(pytz.utc)
