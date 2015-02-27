from enum import IntEnum
import random
import time

from Action import Action


class HuntingGround(IntEnum):
    Island = 0
    Sewers = 1


# todo Combat Skin
class combat:
    def __init__(self, tec):
        self.tec = tec
        self.rotation = [['zzh', 'zxh', 'zch', 'zvh', 'zbh', 'znh', 'zmh', 'za', 'zsh'],
                         ['zz', 'zx', 'zc', 'zv', 'zb', 'zn', 'za', 'za', 'zs']]
        self.free = True
        self.retreat = False
        self.hunting_ground = HuntingGround.Sewers

    def recover(self):
        self.tec.send_cmd("get dag")
        time.sleep(random.randrange(1234, 2512) / 1000)
        self.tec.send_cmd("wie dag")

    def handle_recover(self, recoverNow):
        self.tec.add_action(Action.recover)
        if recoverNow:
            self.perform_action()

    def attack(self):
        index = random.randrange(0, len(self.rotation[self.hunting_ground]) - 1)
        cmd = self.rotation[self.hunting_ground][index]
        self.tec.send_cmd(cmd)
        self.tec.add_action(Action.attack)

    def combat_release(self):
        pass


    def retreat(isRetreating):
        retreat = isRetreating
        pass

    def perform_action(self):
        if self.free and len(self.tec.queue) > 0:
            self.action = self.tec.queue.pop()
            if self.action == Action.recover:
                self.recover()
            elif self.action == Action.retreat:
                self.free = False
            elif self.action == Action.kill:
                self.free = False
                self.tec.add_action(Action.kill)
                self.tec.send_cmd("kl")
            elif self.action == Action.attack:
                self.free = False
                self.attack()
            elif self.action == Action.release:
                self.tec.send_cmd("release")
                pass

    # We are in combat
    def handle_combat_line(self, line):
        me = True
        if "[" in line:
            if "] A" in line or "] An" in line:
                self.tec.add_action(Action.attack)
                me = False
                if self.free:
                    print("Free, attacking")
                    self.perform_action()
            elif "You slit" in line:
                print("Killed")
                self.tec.remove_action(Action.kill)
                self.tec.add_action(Action.skin)
                self.tec.in_combat = False
            roll = self.tec.rollPattern.search(line)
            if me:
                self.action_status = int(roll.group(1)) < int(roll.group(2))

        if "expires." in line:
            self.tec.remove_action(Action.kill)
            self.tec.add_action(Action.skin)
            print("Dead")
            self.tec.in_combat = False
        elif "falls unconscious" in line:
            print("Unconscious")
            self.tec.remove_action(Action.attack)
            self.tec.add_action(Action.kill)
        elif line.strip() == "You are no longer busy.":
            self.free = True
            self.perform_action()
        elif "You fumble!" in line:
            self.handle_recover(False)
        elif "You must be wielding a weapon to attack." in line or "You can't do that right now." in line:
            self.handle_recover(True)
        elif "clamped onto you" in line:
            self.tec.add_action(Action.release)
        elif "You manage to break free!" in line:
            self.tec.remove_action(Action.release)