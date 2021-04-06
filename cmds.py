from time import time
import misc, economy, games, mod, tetueSrc, user_management, automod

PREFIXMSG = tetueSrc.get_string_element("general", "prefix_msg")
PREFIXTWE = tetueSrc.get_string_element("general", "prefix_twe")
PREFIXBUTLER = tetueSrc.get_string_element("tea_butler", "prefix_butler")

class Cmd(object):
    def __init__(self, callables, func, function_info, rights = user_management.Badge.Tueftlie, cooldown=0):
        self.callables = callables
        self.func = func
        self.cooldown = cooldown
        self.next_use = time()
        self.allowed = True
        self.function_info = function_info
        self.rights = rights

cmds = [
    #	misc
    Cmd(["shutdown"], misc.shutdown, "misc"),
    Cmd(["lost", "lostcounter"], misc.lostcounter, "misc", cooldown=5),
    Cmd(["liebe","love"], misc.love, "misc"),
    Cmd(["lurch", "lurk", "lörk"], misc.lurk, "misc"),
    Cmd(["bye"], misc.bye, "misc"),
    Cmd(["state", "statement"], misc.state, "misc"),
    Cmd(["win"], misc.win, "misc", cooldown=30),
    Cmd(["lose"], misc.lose, "misc", cooldown=30),
    Cmd(["modlove", "ml"], misc.modlove, "misc"),
    Cmd(["hug"], misc.hug, "misc"),
    Cmd(["hype"], misc.hype, "misc"),
    #	economy
    Cmd(["coins", "money"], economy.coins, "economy"),

    #	games
    Cmd(["coinflip", "flip"], games.coinflip, "games", cooldown=5),
    Cmd(["competition"], games.competition, "games"),
    Cmd(["tee", "tea", "kaffee", "coffee"], games.new_tea, "games"),

    #	mod
    Cmd(["warn"], mod.warn, "mod"),
    Cmd(["unwarn", "rmwarn"], mod.remove_warn, "mod"),
    Cmd(["gameon"], mod.set_games_on, "mod"),
    Cmd(["gameoff"], mod.set_games_off, "mod"),
    Cmd(["reminder", "rm"], misc.reminder, "mod", user_management.Badge.ManuVIP)
]

def process(bot, user, message):
    if message.startswith(PREFIXMSG):
        cmd = message.split(" ")[0][len(PREFIXMSG):].lower()
        if len(cmd) <= 1: return
        args = message.split(" ")[1:]
        perform(bot, user, cmd, *args)
    elif message.startswith(PREFIXTWE) and user.badge.value <= user_management.Badge.AutoVIP.value:
        hashtag = message.split(" ")[0].lower()
        args = message.split(" ")[1:]
        misc.register_hastag(bot, user, hashtag, *args)
    elif message.startswith(PREFIXBUTLER):
        butler = message.split(" ")[0][len(PREFIXBUTLER):].lower()
        args = message.split(" ")[1:]
        if butler != bot.USERNAME: return
        games.process_tea_butler(bot, user, *args)

def perform(bot, user, call, *args):
    if call in ("help", "commands", "cmds"):
        misc.help(bot, PREFIXMSG, cmds)
    else:
        if PREFIXMSG in call: return # Sortiere Nachrichten aus wie <!!!>
        for cmd in cmds:
            if call in cmd.callables:
                if cmd.allowed != True: return # cmd ist gerade nicht erlaubt
                if user.badge.value > cmd.rights.value: return # Darf user das Kommando überhaupt ausführen
                if time() > cmd.next_use:
                    cmd.func(bot, user, *args)
                    cmd.next_use = time() + cmd.cooldown
                else:
                    bot.send_message(f"Cooldown ist noch aktiv. Versuch es in {cmd.next_use-time():,.0f} Sekunde(n) noch einmal.")

                return
        if automod.check_spam_cmd(bot, user) == True:
            bot.send_message(f"{user.get_displayname()}, \"{call}\" ist kein gültiger Befehl.")