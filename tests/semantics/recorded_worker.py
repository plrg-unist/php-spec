"""Checked worker transport with exact packet, stderr and closure evidence."""
import json
import signal
import subprocess
import static_types as types


def expired(signum, frame):
    raise TimeoutError("checked worker exceeded 30 seconds")


class Worker:
    def __init__(self, command, output):
        self.output = output
        output.mkdir()
        (output / 'command.json').write_text(json.dumps(command) + '\n')
        self.stderr = (output / 'stderr').open('xb')
        self.p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=self.stderr, env=types.ENV)
        self.sequence = 0

    def request(self, request):
        stem = self.output / str(self.sequence)
        self.sequence += 1
        packet = (types.wire.dumps(request) + '\n').encode('utf-8')
        with stem.with_suffix('.request').open('xb') as raw:
            raw.write(packet)
        previous = signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, 30)
        try:
            self.p.stdin.write(packet)
            self.p.stdin.flush()
            response = bytearray()
            with stem.with_suffix('.response').open('xb') as raw:
                while not response.endswith(b'\n'):
                    chunk = self.p.stdout.read1(65536)
                    if not chunk:
                        raise EOFError('worker closed before its response packet')
                    raw.write(chunk)
                    raw.flush()
                    response.extend(chunk)
            result = types.wire.loads(response.decode('utf-8'))
            assert result['ok'], result
            return result
        except BaseException as error:
            stem.with_suffix('.exception.json').write_text(json.dumps(
                {'type': type(error).__name__, 'message': str(error)}) + '\n')
            raise
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)

    def close(self):
        status = {}
        try:
            self.p.stdin.close()
            self.p.stdin = None
            stdout, _ = self.p.communicate(timeout=5)
            (self.output / 'trailing.stdout').write_bytes(stdout)
            status = {'status': 'exit', 'exit_status': self.p.returncode}
            assert self.p.returncode == 0, status
            assert not stdout, 'worker emitted trailing stdout'
            self.stderr.flush()
            assert not (self.output / 'stderr').read_bytes(), 'worker emitted stderr'
        except BaseException as error:
            status.update({'exception': type(error).__name__, 'message': str(error)})
            if isinstance(error, subprocess.TimeoutExpired):
                (self.output / 'trailing.stdout').write_bytes(error.stdout or b'')
            raise
        finally:
            if self.p.poll() is None:
                self.p.kill()
                self.p.wait(timeout=5)
            status['final_exit_status'] = self.p.returncode
            (self.output / 'close.json').write_text(json.dumps(status) + '\n')
            self.stderr.close()
