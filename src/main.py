import sys
from preproc import *
from projections import *

config = {}

def print_opt():
    print("\nSelect an option:")
    print("1 - Build Rosters")
    print("2 - Build Stats")
    print("3 - Build Caps")

    print("sc - set team cap space")
    print("sf - set rem. required forwards")
    print("sd - set rem. required defenders")
    print("sg - set rem. required goalies")

    print("d - Other team drafter play [--ID--}]")
    print("dr - Revoke other team drafted player (mistake) [--ID--]")
    print("a - Assign player to my team [--ID--]")
    print("ar - Revoke assign player to my team (mistake) [--ID--]")

    print("p - Calculate my team roster projections")
    print("o - Optimize draft picks")

    print("E - Exit\n")

def main():
    while True:
        print_opt()
        arg = input("Enter option (E to exit): ").strip()
        match arg:
            case "1":
                build_rosters()
            case "2":
                build_stats()
            case "3":
                build_caps()

            case "sc":
                config["cap_space"] = 0
            case "sf":
                config["rem_f"] = 0
            case "sd":
                config["rem_d"] = 0
            case "sg":
                config["rem_g"] = 0

            case "d":
                return
            case "dr":
                return
            case "a":
                return
            case "ar":
                return
            
            case "p":
                return
            case "o":
                return
            
            case "E" | "e":
                print("Exiting...")
                break
            case _:
                print("Invalid option, try again.")


if __name__ == "__main__":
    main()