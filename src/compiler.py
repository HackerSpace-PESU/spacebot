import os
import pydoodle
from dotenv import load_dotenv

load_dotenv()

COMPILER_CLIENT_ID_1 = os.environ['COMPILER_CLIENT_ID_1']
COMPILER_CLIENT_SECRET_1 = os.environ['COMPILER_CLIENT_SECRET_1']
COMPILER_CLIENT_ID_2 = os.environ['COMPILER_CLIENT_ID_2']
COMPILER_CLIENT_SECRET_2 = os.environ['COMPILER_CLIENT_SECRET_2']
COMPILER_CLIENT_ID_3 = os.environ['COMPILER_CLIENT_ID_3']
COMPILER_CLIENT_SECRET_3 = os.environ['COMPILER_CLIENT_SECRET_3']
COMPILER_CLIENT_ID_4 = os.environ['COMPILER_CLIENT_ID_4']
COMPILER_CLIENT_SECRET_4 = os.environ['COMPILER_CLIENT_SECRET_4']
COMPILER_CLIENT_ID_5 = os.environ['COMPILER_CLIENT_ID_5']
COMPILER_CLIENT_SECRET_5 = os.environ['COMPILER_CLIENT_SECRET_5']


compiler_keys = {
    (COMPILER_CLIENT_ID_1, COMPILER_CLIENT_SECRET_1): 0,
    (COMPILER_CLIENT_ID_2, COMPILER_CLIENT_SECRET_2): 0,
    (COMPILER_CLIENT_ID_3, COMPILER_CLIENT_SECRET_3): 0,
    (COMPILER_CLIENT_ID_4, COMPILER_CLIENT_SECRET_4): 0,
    (COMPILER_CLIENT_ID_5, COMPILER_CLIENT_SECRET_5): 0,
}


def checkSpamCode(script, inputs=None):
    if isinstance(inputs, str):
        return "@everyone" in script or "@here" in script or "@everyone" in inputs or "@here" in inputs or '@&' in script or '@&' in inputs
    else:
        return "@everyone" in script or "@here" in script or '@&' in script


async def executeCode(COMPILER_CLIENT_ID, COMPILER_CLIENT_SECRET, script, language, inputs=None):
    executor = pydoodle.Compiler(
        clientId=COMPILER_CLIENT_ID, clientSecret=COMPILER_CLIENT_SECRET)
    output = executor.execute(script=script, language=language, stdIn=inputs)
    return output


async def updateCodeAPICallLimits(COMPILER_CLIENT_ID, COMPILER_CLIENT_SECRET):
    executor = pydoodle.Compiler(
        clientId=COMPILER_CLIENT_ID, clientSecret=COMPILER_CLIENT_SECRET)
    return 200 - executor.usage()
