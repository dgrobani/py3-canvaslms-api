#  http://stackoverflow.com/a/21686937 & http://stackoverflow.com/a/1262210

from canvas.core.accounts import all_programs
from canvas.core.io import get_cmi_clos_by_program  # BROKEN?

from canvas.core.etc import scrub

programs = []
for program in programs or all_programs('synergis_yes'):
    print('\n' + program)
    for clo in get_cmi_clos_by_program(program):
        scrubbed = scrub(clo['clo_description'])
        if clo['clo_description'] != scrubbed:
            print(clo['clo_title'])
            print(clo['clo_description'])
            print(scrubbed)
