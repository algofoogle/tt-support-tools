import git
import os
from urllib.parse import urlparse

MAX_ROM_TEXT_SIZE = 92

segment_font = {
    " ": 0b00000000,
    "0": 0b00111111,
    "1": 0b00000110,
    "2": 0b01011011,
    "3": 0b01001111,
    "4": 0b01100110,
    "5": 0b01101101,
    "6": 0b01111101,
    "7": 0b00000111,
    "8": 0b01111111,
    "9": 0b01101111,
    "A": 0b01110111,
    "B": 0b01111100,
    "C": 0b00111001,
    "D": 0b01011110,
    "E": 0b01111001,
    "F": 0b01110001,
    "t": 0b01111000,
}

def segment_char(c):
    return segment_font[c]

class ROMFile:
    def __init__(self, config, projects):
        self.projects = projects
        self.config = config

    def get_git_remote(self):
        repo_url = list(git.Repo(".").remotes[0].urls)[0]
        return urlparse(repo_url).path[1:]

    def get_git_commit_hash(self):
        return git.Repo(".").commit().hexsha

    def write_rom(self):
        rom = bytearray(256)
        short_sha = self.get_git_commit_hash()[:8]

        rom_text = f"shuttle={self.config['id']}\n"
        rom_text += f"repo={self.get_git_remote()}\n"
        rom_text += f"commit={short_sha}\n"

        print(f"\nROM text: {len(rom_text)} bytes (max={MAX_ROM_TEXT_SIZE})\n")
        print("  " + "\n  ".join(rom_text.split("\n")))

        assert len(rom_text) < MAX_ROM_TEXT_SIZE, "ROM text too long"

        rom[0:4] = map(segment_char, self.config['id'])
        rom[8:16] = map(segment_char, short_sha.upper())
        rom[32 : 32 + len(rom_text)] = rom_text.encode("ascii")

        with open(os.path.join(os.path.dirname(__file__), "rom/rom.vmem"), "w") as fh:
            for line in rom_text.split("\n"):
                if len(line) == 0:
                    continue
                fh.write(f"// {line}\n")
            fh.write("\n")
            for line in range(0, len(rom), 16):
                for byte in range(0, 16):
                    fh.write("{:02x} ".format(rom[line + byte]))
                fh.write("\n")
