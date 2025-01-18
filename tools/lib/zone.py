# TODO: Implement or import these utilities as needed
def get_line(file_obj):
    """
    Mimic the get_line(FILE *fl, char *buf) behavior:
    - Reads a single line from file_obj.
    - Returns the line stripped of trailing newline.
    - Returns None or empty if EOF is reached.
    - For convenience, might also return the number of lines read (1 or 0).
    """
    # Example stub implementation:
    line = file_obj.readline()
    if not line:
        return None, 0
    return line.rstrip('\n'), 1


def skip_spaces(line):
    """
    Mimic skip_spaces(&ptr) by returning the string with leading
    whitespace removed.
    """
    return line.lstrip() if line else line


def log(message, *args):
    """
    Mimic the log() function. 
    In CircleMUD, this would typically log to syslog or mudlog. 
    In Python, we might just use print, or logging module, etc.
    """
    print(message % args if args else message)


def exit_with_error(code=1):
    """
    Mimic exit(1) from C.
    """
    import sys
    sys.exit(code)


class ResetCommand:
    """
    Python equivalent of 'struct reset_com' with the fields used in the code.
    """
    def __init__(self):
        self.command = None
        self.if_flag = 0
        self.arg1 = 0
        self.arg2 = 0
        self.arg3 = 0
        self.line = 0
        self.command_comment = ""


class ZoneData:
    """
    Python class to hold zone information.
    """
    def __init__(self):
        self.number = 0
        self.name = ""
        self.bot = 0
        self.top = 0
        self.lifespan = 0
        self.reset_mode = 0
        self.cmd = []  # Will hold a list of ResetCommand objects


# Pretend we have a global table or a variable to track the top of the zone table
top_of_zone_table = 0


def load_zones(file_obj, zonename):
    """
    Rough Python translation of the CircleMUD load_zones() function.
    Reads zone information from an open file object (file_obj).
    """
    global top_of_zone_table

    # Static-like variable from C:
    # 'static zone_rnum zone = 0;' 
    # Python won't keep static across calls in the same way,
    # but we'll mimic by making it global or using an outer scope tracker.
    # For demonstration, let's assume we have a global or external
    # variable that increments each time we load a zone.
    zone_rnum = top_of_zone_table  

    # Create a new zone data object
    zone_data = ZoneData()

    # We'll keep track of how many lines we've read
    line_num = 0
    num_of_cmds = 0

    # Skip first 3 lines (as in the original C code)
    for _ in range(3):
        line, lines_read = get_line(file_obj)
        line_num += lines_read

    # Count how many commands are in the zone
    while True:
        position = file_obj.tell()  # remember file position
        line, lines_read = get_line(file_obj)
        if not line:
            # Reached EOF
            break

        # We only increment line_num after we confirm there's a line
        line_num += lines_read

        if ((line[0] in "MOPGERD" and len(line) > 1 and line[1] == ' ')
                or (line[0] == 'S' and len(line) == 1)):
            num_of_cmds += 1

        # Move the file pointer back so we can read the lines again
        file_obj.seek(position)
        break  # break out of loop so we don't skip reading lines again

    # We need to continue scanning the file to count all commands
    while True:
        position = file_obj.tell()
        line, lines_read = get_line(file_obj)
        if not line:
            break
        line_num += lines_read

        if ((line[0] in "MOPGERD" and len(line) > 1 and line[1] == ' ')
                or (line[0] == 'S' and len(line) == 1)):
            num_of_cmds += 1

    # Rewind the file
    file_obj.seek(0)
    line_num = 0  # reset line count for our real read

    # If no commands, bail out
    if num_of_cmds == 0:
        log("SYSERR: %s is empty!", zonename)
        exit_with_error(1)

    # In C, we'd do: CREATE(Z.cmd, struct reset_com, num_of_cmds)
    # In Python, we don't need to allocate upfront.

    # Read the first line (should be '#<zone_number>')
    line, lines_read = get_line(file_obj)
    line_num += lines_read
    if not line:
        log("SYSERR: Empty file when expecting zone header: %s", zonename)
        exit_with_error(1)

    # Expecting something like "#123"
    if not line.startswith("#"):
        log("SYSERR: Format error in %s, line %d", zonename, line_num)
        exit_with_error(1)

    # Parse the zone number
    # In the C code: sscanf(buf, "#%hd", &Z.number)
    try:
        zone_data.number = int(line[1:])  # skip '#'
    except ValueError:
        log("SYSERR: Format error in %s, line %d", zonename, line_num)
        exit_with_error(1)

    # Next line is the zone name (may have a '~' to strip)
    line, lines_read = get_line(file_obj)
    line_num += lines_read
    if line is None:
        log("SYSERR: Unexpected EOF reading zone name in %s", zonename)
        exit_with_error(1)

    # If there's a '~', strip it
    idx = line.find('~')
    if idx != -1:
        line = line[:idx]
    zone_data.name = line

    # Next line should have 4 numeric constants: bot, top, lifespan, reset_mode
    line, lines_read = get_line(file_obj)
    line_num += lines_read
    if line is None:
        log("SYSERR: Unexpected EOF reading numeric constants in %s", zonename)
        exit_with_error(1)

    # C code: sscanf(buf, " %hd %hd %d %d ", &Z.bot, &Z.top, &Z.lifespan, &Z.reset_mode)
    try:
        parts = line.split()
        zone_data.bot = int(parts[0])
        zone_data.top = int(parts[1])
        zone_data.lifespan = int(parts[2])
        zone_data.reset_mode = int(parts[3])
    except (IndexError, ValueError):
        log("SYSERR: Format error in numeric constant line of %s", zonename)
        exit_with_error(1)

    if zone_data.bot > zone_data.top:
        log("SYSERR: Zone %d bottom (%d) > top (%d).", 
            zone_data.number, zone_data.bot, zone_data.top)
        exit_with_error(1)

    # Now read the commands
    cmd_no = 0
    while True:
        line, lines_read = get_line(file_obj)
        if line is None:
            # Reached EOF unexpectedly
            log("SYSERR: Format error in %s - premature end of file", zonename)
            exit_with_error(1)
        line_num += lines_read

        line = skip_spaces(line)

        if not line:
            # empty line or comment, just skip
            continue

        cmd_char = line[0]

        # If line starts with '*', it's a comment
        if cmd_char == '*':
            continue

        # If 'S' or '$', we set the command to 'S' and break
        if cmd_char in ['S', '$']:
            # This matches the C code: if (ZCMD.command == 'S' || ZCMD.command == '$')
            # we treat it as a 'S' command and break from reading more commands
            reset_cmd = ResetCommand()
            reset_cmd.command = 'S'
            zone_data.cmd.append(reset_cmd)
            break

        # Otherwise, parse the command
        reset_cmd = ResetCommand()
        reset_cmd.command = cmd_char

        # The rest of the line is after the command char
        args_str = line[1:].strip()

        # The code checks if the command is one that takes 3 arguments vs 4
        # In the C code, 3-arg commands are "G E R" etc., 4-arg commands are "M O P D"
        # Actually, the snippet says: if (strchr("MOEPD", ZCMD.command) == NULL) ...
        # i.e. if command is NOT in "MOEPD", it uses the 3-arg version,
        # else it uses the 4-arg version.
        '''
        if cmd_char not in "MOEPD":
            # 3-arg command
            try:
                # Format: if_flag arg1 arg2
                parts = args_str.split()
                reset_cmd.if_flag = int(parts[0])
                reset_cmd.arg1 = int(parts[1])
                reset_cmd.arg2 = int(parts[2])
            except (IndexError, ValueError):
                log("SYSERR: Format error in %s, line %d: '%s'", zonename, line_num, line)
                exit_with_error(1)
        else:
            # 4-arg command
            try:
                # Format: if_flag arg1 arg2 arg3
                parts = args_str.split()
                reset_cmd.if_flag = int(parts[0])
                reset_cmd.arg1 = int(parts[1])
                reset_cmd.arg2 = int(parts[2])
                reset_cmd.arg3 = int(parts[3])
            except (IndexError, ValueError):
                log("SYSERR: Format error in %s, line %d: '%s'", zonename, line_num, line)
                exit_with_error(1)

        reset_cmd.line = line_num
        zone_data.cmd.append(reset_cmd)
        cmd_no += 1
        '''
        
        import re

        if cmd_char in "MOEPD":
            # Expect exactly 4 integers + optional trailing text
            # We'll use a regex to capture up to 4 integers, plus the leftover
            match = re.match(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)(.*)$', args_str)
            if not match:
                log("SYSERR: Format error in %s, line %d: '%s'", zonename, line_num, line)
                exit_with_error(1)

            reset_cmd.if_flag = int(match.group(1))
            reset_cmd.arg1   = int(match.group(2))
            reset_cmd.arg2   = int(match.group(3))
            reset_cmd.arg3   = int(match.group(4))

            # leftover is group(5)
            leftover = match.group(5).strip()
            reset_cmd.command_comment = leftover  # store e.g. "Puff"
        else:
            # Expect exactly 3 integers + optional trailing text
            match = re.match(r'^\s*(\d+)\s+(\d+)\s+(\d+)(.*)$', args_str)
            if not match:
                log("SYSERR: Format error in %s, line %d: '%s'", zonename, line_num, line)
                exit_with_error(1)

            reset_cmd.if_flag = int(match.group(1))
            reset_cmd.arg1   = int(match.group(2))
            reset_cmd.arg2   = int(match.group(3))

            # leftover is group(4)
            leftover = match.group(4).strip()
            reset_cmd.command_comment = leftover

        zone_data.cmd.append(reset_cmd)
        cmd_no += 1

    # We expect num_of_cmds to match cmd_no + 1
    # (the +1 presumably for the final 'S' command)
    if num_of_cmds != cmd_no + 1:
        log("SYSERR: Zone command count mismatch for %s. Estimated: %d, Actual: %d",
            zonename, num_of_cmds, cmd_no + 1)
        exit_with_error(1)

    # Finally, increment our "top_of_zone_table"
    top_of_zone_table = zone_rnum + 1

    # Return the zone data (or you could store it globally, etc.)
    return zone_data


# Example usage:
# with open('some_zone_file.zon', 'r') as f:
#     zone_info = load_zones(f, 'some_zone_file.zon')
#     # Now 'zone_info' holds the parsed data
