import subprocess
import logging, time

logger = logging.getLogger()

def runCmd(cmd, cwd=None):
    return runCmdWithOutput(cmd, cwd)

def runCMD(cmd, out_file, err_file, cwd=None):
    start_time = time.time()
    logger.info(f"cmd to run: {cmd}")

    subprocess.run(cmd, shell=True, cwd=cwd, stdout=out_file, stderr=err_file)
    
    logger.info(f"cmd execution time: {time.time() - start_time}")

def runCmdWithOutput(cmd, cwd=None):
    start_time = time.time()
    logger.info(f"cmd to run: {cmd}")
    p = subprocess.run(cmd,
                       shell=True,
                       cwd=cwd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    try:
        output = p.stdout.decode('utf-8')
    except UnicodeDecodeError:
        logger.warn("cmd UnicodeDecodeError")
        output = p.stdout.decode('unicode_escape')

    error = p.stderr.decode('utf-8')
    if len(error) > 0:
        logger.error(f"output error: {error}")

    if len(output) > 0:
        logger.info(f"output of this cmd: {output}")

    logger.info(f"cmd execution time: {time.time() - start_time}")
    return output

def runCmdWithOutputWithoutLog(cmd, cwd=None):
    """
    only return output, with no cmd basic info print to the console
    """
    p = subprocess.run(cmd,
                       shell=True,
                       cwd=None,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    try:
        output = p.stdout.decode('utf-8')
    except UnicodeDecodeError:
        logger.warn("cmd UnicodeDecodeError")
        output = p.stdout.decode('unicode_escape')

    return output


def runCmdWithoutOutput(cmd, cwd=None):
    start_time = time.time()
    logger.info(f"cmd to run: {cmd}")

    return_code = subprocess.call(cmd, shell=True, cwd=cwd)

    logger.info(f"cmd execution time: {time.time() - start_time}")
    return return_code
