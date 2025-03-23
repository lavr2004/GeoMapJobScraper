from bin.parsers.pracujpl.pracujpl import PracujPLParser
from bin.parsers.urzadpracy.urzadpracy import UrzadparcyParser
from bin.parsers.pracujpl_all.pracujpl_all import PracujPLAllWarszawaParser

def main():
    #launch_parser_pracujpl()
    launch_parser_urzadpracy()
    #launch_parser_pracujpl_all_warszawa()

def launch_parser_pracujpl_all_warszawa():
    parser = PracujPLAllWarszawaParser()

    parser.parse(1)

    parser.update_coordinates()

    parser.commit_changes()

    print(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    print("=" * 100)

def launch_parser_pracujpl():
    parser = PracujPLParser()

    # Parsing multiple pages
    for page in range(0, 6):
        parser.parse(page)

        # Update job vacancies with coordinates
    parser.update_coordinates()

    # Commit changes to the database
    parser.commit_changes()
    print(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    print("=" * 100)

def launch_parser_urzadpracy():
    parser = UrzadparcyParser()
    parser.parse()
    parser.commit_changes()
    print(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    print("=" * 100)

if __name__ == "__main__":
    main()
