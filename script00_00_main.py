from bin.parsers.pracujpl.pracujpl import PracujPLParser
from bin.parsers.urzadpracy.urzadpracy import UrzadparcyParser
from bin.parsers.pracujpl_all.pracujpl_all import PracujPLAllWarszawaParser

from bin.settings import get_logger_fc

def exec_try_except(fc):
    try:
        fc()
    except Exception as e:
        print(e)

def main():
    #launch_parser_pracujpl()
    #launch_parser_pracujpl_all_warszawa()
    exec_try_except(launch_parser_urzadpracy)
    #exec_try_except(launch_parser_pracujpl_all_warszawa)



def launch_parser_pracujpl_all_warszawa():

    pracujplallwarszawa_logger = get_logger_fc("pracujplallwarszawa")

    parser = PracujPLAllWarszawaParser(pracujplallwarszawa_logger)

    parser.parse(1)

    parser.update_coordinates()

    parser.commit_changes()

    pracujplallwarszawa_logger.info(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    pracujplallwarszawa_logger.info("=" * 100)

def launch_parser_pracujpl():
    pracujplall_logger = get_logger_fc("pracujplall")

    parser = PracujPLParser(pracujplall_logger)

    # Parsing multiple pages
    for page in range(0, 6):
        parser.parse(page)

        # Update job vacancies with coordinates
    parser.update_coordinates()

    # Commit changes to the database
    parser.commit_changes()
    pracujplall_logger.info(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    pracujplall_logger.info("=" * 100)

def launch_parser_urzadpracy():
    urzadpracy_logger = get_logger_fc("urzadpracy")

    parser = UrzadparcyParser(urzadpracy_logger)
    parser.parse()
    parser.commit_changes()
    urzadpracy_logger.info(f"OK: parsing {parser.PLATFORMNAME_STR} finished")
    urzadpracy_logger.info("=" * 100)

if __name__ == "__main__":
    main()
