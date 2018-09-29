"""
Support for Yamaha NP Radios.
For more details about this platform, please refer to the documentation at
https://abelnlindenschmidt.de
"""

import logging

import requests
import voluptuous as vol
from xml.etree import ElementTree as ET

from homeassistant.components.media_player import (
    MEDIA_TYPE_MUSIC, PLATFORM_SCHEMA, SUPPORT_NEXT_TRACK, SUPPORT_PAUSE,
    SUPPORT_PLAY, SUPPORT_PREVIOUS_TRACK, SUPPORT_STOP, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET,
    MediaPlayerDevice)
from homeassistant.const import (
    CONF_HOST, STATE_IDLE, STATE_OFF)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

ICON = 'mdi:radio'
url = "http://192.168.178.10/YamahaRemoteControl/ctrl"

PowerStatus = "<YAMAHA_AV cmd=\"GET\"><System><Power_Control><Power>GetParam</Power></Power_Control></System></YAMAHA_AV>"
PowerOn = "<YAMAHA_AV cmd=\"PUT\"><System><Power_Control><Power>On</Power></Power_Control></System></YAMAHA_AV>"
PowerOff = "<YAMAHA_AV cmd=\"PUT\"><System><Power_Control><Power>Standby</Power></Power_Control></System></YAMAHA_AV>"
PlayStatus = "<YAMAHA_AV cmd=\"GET\"><Player><Play_Info>GetParam</Play_Info></Player></YAMAHA_AV>"
Status = "<YAMAHA_AV cmd=\"GET\"><System><Basic_Status>GetParam</Basic_Status></System></YAMAHA_AV>"
Volume = "'<YAMAHA_AV cmd=\"PUT\"><System><Volume><Lvl>' + volset + '</Lvl></Volume></System></YAMAHA_AV>'"
Features = "<YAMAHA_AV cmd=\"GET\"><System><Config>GetParam</Config></System></YAMAHA_AV>"
Play = "<YAMAHA_AV cmd=\"PUT\"><Player><Play_Control><Playback>Play</Playback></Play_Control></Player></YAMAHA_AV>"
Pause = "<YAMAHA_AV cmd=\"PUT\"><Player><Play_Control><Playback>Pause</Playback></Play_Control></Player></YAMAHA_AV>"
Next = "<YAMAHA_AV cmd=\"PUT\"><Player><Play_Control><Playback>Next</Playback></Play_Control></Player></YAMAHA_AV>"
Prev = "<YAMAHA_AV cmd=\"PUT\"><Player><Play_Control><Playback>Prev</Playback></Play_Control></Player></YAMAHA_AV>"
Mutecom = "<YAMAHA_AV cmd=\"PUT\"><System><Volume><Mute>On</Mute></Volume></System></YAMAHA_AV>"

headers = {
    'Content-Type': "text/xml",
    'Cache-Control': "no-cache",
    'Postman-Token': "9ad57fc1-4c78-a921-5967-bef4d2167214"
}

SUPPORT_YAMAHANP = SUPPORT_PLAY | SUPPORT_PAUSE | SUPPORT_STOP | \
                     SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_TURN_ON | \
                     SUPPORT_TURN_OFF | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default='192.168.178.10'): cv.string,
    vol.Required(CONF_NAME, default='Yamaha NP'): cv.string,
})

class YamahaNPDevice(MediaPlayerDevice):
    """Representation of a Logitech UE Smart Radio device."""

    def __init__(self, name, player_id, version_name):
        """Initialize the Logitech UE Smart Radio device."""
        self._player_id = player_id
        self._version_name = version_name
        self._name = name
        self._state = None
        self._volume = 0
        self._media_title = None
        self._media_artist = None
        self._media_album_name = None
        self._muted = False

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Logitech UE Smart Radio platform."""
    features = config.get(CONF_HOST)

    responsez = requests.request("POST", url, data=Features, headers=headers)
    treea = ET.fromstring(responsez.content)
    for featuresv in treea.findall('.//Model_Name'):
        namea = featuresv

    responsey = requests.request("POST", url, data=Features, headers=headers)
    treeb = ET.fromstring(responsey.content)
    for featuresa in treeb.findall('.//System_ID'):
        system_id = faturesa.text

    responsex = requests.request("POST", url, data=Features, headers=headers)
    treec = ET.fromstring(responsex.content)
    for featuresb in treec.findall('.//Version'):
        version_name = featuresb.text

    add_entities([YamahaNPDevice(namea, system_id, version_name)])

def update(self):
    """Get the latest details from the device."""
# pwstate
    responsea = requests.request("POST", url, data=PowerStatus, headers=headers)
    treed = ET.fromstring(responsea.content)
    for power_name in treed.findall('.//Power_Control/Power'):
        self._pwstate = power_name.text

    if self._pwstate == "On":
        self._state = STATE_IDLE
    else:
        self._state = STATE_OFF

    # volumestate
    responseb = requests.request("POST", url, data=Status, headers=headers)
    treee = ET.fromstring(responseb.content)
    for vol_number in treee.findall('.//Volume/Lvl'):
        self._volume = vol_number.text


    # titel
    responsec = requests.request("POST", url, data=PlayStatus, headers=headers)
    treef = ET.fromstring(responsec.content)
    for music_title in treef.findall('.//Meta_Info/Song'):
        self._media_title = music_title.text

    # album
    responsed = requests.request("POST", url, data=PlayStatus, headers=headers)
    treeg = ET.fromstring(responsed.content)
    for album_name in treeg.findall('.//Meta_Info/Album'):
        self._media_album_name = album_name.text

    # Kunstler
    responsee = requests.request("POST", url, data=PlayStatus, headers=headers)
    treeh = ET.fromstring(responsee.content)
    for artist_name in treeh.findall('.//Meta_Info/Artist'):
        self._media_artist = artist_name.text


    # mutestate
    responsef = requests.request("POST", url, data=Status, headers=headers)
    treei = ET.fromstring(responsef.content)
    for volm_name in treei.findall('.//Volume/Mute'):
        resultf = volm_name.text
        if resultf == "On":
            self._muted = True
        if resultf == "Off":
            self._muted = False



@property
def name(self):
    """Return the name of the device."""
    return self._name


@property
def state(self):
    """Return the state of the device."""
    return self._state


@property
def icon(self):
    """Return the icon to use in the frontend, if any."""
    return ICON


@property
def is_volume_muted(self):
    """Boolean if volume is currently muted."""
    return self._muted


@property
def volume_level(self):
    """Volume level of the media player (0..1)."""
    return self._volume


@property
def supported_features(self):
    """Flag of features that are supported."""
    return SUPPORT_YAMAHANP


@property
def media_content_type(self):
    """Return the media content type."""
    return MEDIA_TYPE_MUSIC

@property
def media_artist(self):
    """Artist of current playing media, music track only."""
    return self._media_artist


@property
def media_title(self):
    """Title of current playing media."""
    return self._media_title


@property
def media_album_name(self):
    """Title of current playing media."""
    return self._media_album_name


def turn_on(self):
    """Turn on specified media player or all."""
    requests.request("POST", url, data=PowerOn, headers=headers)


def turn_off(self):
    """Turn off specified media player or all."""
    requests.request("POST", url, data=PowerOff, headers=headers)


def media_play(self):
    """Send the media player the command for play/pause."""
    requests.request("POST", url, data=Play, headers=headers)


def media_pause(self):
    """Send the media player the command for pause."""
    requests.request("POST", url, data=Pause, headers=headers)


def media_stop(self):
    """Send the media player the stop command."""
    requests.request("POST", url, data=Pause, headers=headers)


def media_previous_track(self):
    """Send the media player the command for prev track."""
    requests.request("POST", url, data=Next, headers=headers)


def media_next_track(self):
    """Send the media player the command for next track."""
    requests.request("POST", url, data=Prev, headers=headers)


def mute_volume(self, mute):
    """Send mute command."""
    if mute:
        requests.request("POST", url, data=Mutecom, headers=headers)
    else:
        requests.request("POST", url, data=Mutecom, headers=headers)


def set_volume_level(self, volume):
    """Set volume level, range 0..1."""
    volset = str(round(volume))
    requests.request("POST", url, data='<YAMAHA_AV cmd=\"PUT\"><System><Volume><Lvl>' + volset + '</Lvl></Volume></System></YAMAHA_AV>',headers=headers)
