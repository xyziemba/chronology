from chronology import cli,config
import time

def test_isDaemonRunning():
    cli.start()
    time.sleep(2) # sleep two seconds to see if the script crashes
    assert config.getChronologyPid() != None
    cli.stop()