from bin.parsers.pracujpl.pracujpl import PracujPLParser
from bin.parsers.urzadpracy.urzadpracy import UrzadparcyParser

def main():
    launch_parser_pracujpl()
    print("=" * 100)
    launch_parser_urzadpracy()

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

def launch_parser_urzadpracy():
    parser = UrzadparcyParser()
    parser.parse()
    parser.commit_changes()
    print(f"OK: parsing {parser.PLATFORMNAME_STR} finished")

if __name__ == "__main__":
    main()
