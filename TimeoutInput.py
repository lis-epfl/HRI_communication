import sys
import time


class TimeoutInput(object):
    def __init__(self, poll_period=0.05):
        import sys, tty, termios  # apparently timing of import is important if using an IDE
        self.poll_period = poll_period

    def _getch_nix(self):
        import sys, tty, termios
        from select import select
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            [i, o, e] = select([sys.stdin.fileno()], [], [], self.poll_period)
            if i:
                ch = sys.stdin.read(1)
            else:
                ch = ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _getch_osx(self):
        # from same discussion on the original ActiveState recipe:
        # http://code.activestate.com/recipes/134892-getch-like-unbuffered-character-reading-from-stdin/#c2
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0] == 0:  # 0x0008 is the keyDownMask
            return ''
        else:
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

    def input(self, prompt=None, timeout=None,
              extend_timeout_with_input=True, require_enter_to_confirm=True):
        """timeout: float seconds or None (blocking)"""
        prompt = prompt or ''
        sys.stdout.write(prompt)  # this avoids a couple of problems with printing
        sys.stdout.flush()  # make sure prompt appears before we start waiting for input
        input_chars = []
        start_time = time.time()
        received_enter = False
        while (time.time() - start_time) < timeout:
            # keep polling for characters
            c = self._getch_osx()  # self.poll_period determines spin speed
            if c in ('\n', '\r'):
                received_enter = True
                break
            elif c:
                input_chars.append(c)
                sys.stdout.write(c)
                sys.stdout.flush()
                if extend_timeout_with_input:
                    start_time = time.time()
        sys.stdout.write('\n')  # just for consistency with other "prints"
        sys.stdout.flush()
        captured_string = ''.join(input_chars)
        if require_enter_to_confirm:
            return_string = captured_string if received_enter else ''
        else:
            return_string = captured_string
        return return_string