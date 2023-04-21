import crunch42.parser as parser


def produce_sarif_from_scan_reports(scanReports):
    sarifArtifactIndices = {}
    sarifResults = []
    sarifFiles = {}
    nextArtifactIndex = 0
    nextRuleIndex = 0
    sarifRuleIndices = {}
    sarifRules = {}
    sarifLog = {
        "version": "2.1.0",
        "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "42Crunch API Conformance Scan",
                        "informationUri": "https://42crunch.com/",
                        "rules": [],
                    },
                },
                "results": sarifResults,
                "artifacts": [],
            },
        ],
    }

    for file, report in scanReports.items():
        for path, pathObj in report["paths"].items():
            for method, methodObj in pathObj.items():
                if "conformanceRequestIssues" in methodObj:
                    for issue in methodObj["conformanceRequestIssues"]:
                        test = issue["test"]
                        if not file in sarifFiles:
                            nextArtifactIndex += 1
                            sarifArtifactIndices[file] = nextArtifactIndex
                            sarifFiles[file] = {
                                "location": {
                                    "uri": file,
                                },
                            }
                        parsedFile = parser.parseFile(file)
                        line, col = parser.getLineAndCol(
                            test["jsonPointer"], parsedFile
                        )
                        sarifRepresentation = {
                            "level": "error",
                            "ruleId": test["key"],
                            "message": {
                                "text": test["description"],
                            },
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {
                                            "uri": file,
                                            "index": sarifArtifactIndices[file],
                                        },
                                        "region": {
                                            "startLine": line,
                                            "startColumn": col,
                                        },
                                    },
                                },
                            ],
                        }
                        if not test["key"] in sarifRules:
                            nextRuleIndex += 1
                            sarifRuleIndices[test["key"]] = nextRuleIndex
                            helpUrl = "https://support.42crunch.com"
                            helpText = "This is a sample entry for scan issue help"
                            sarifRules[test["key"]] = {
                                "id": test["key"],
                                "shortDescription": {
                                    "text": test["description"],
                                },
                                "helpUri": helpUrl,
                                "help": {
                                    "text": helpText,
                                },
                                "properties": {"category": "Other"},
                            }
                        sarifRepresentation["ruleIndex"] = sarifRuleIndices[test["key"]]
                        sarifResults.append(sarifRepresentation)

    if len(sarifFiles.keys()) > 0:
        sarifLog["runs"][0]["artifacts"] = []
        for path in sarifFiles.keys():
            sarifLog["runs"][0]["artifacts"].append(sarifFiles[path])

    if len(sarifRules.keys()) > 0:
        for ruleId in sarifRules.keys():
            sarifLog["runs"][0]["tool"]["driver"]["rules"].append(sarifRules[ruleId])

    return sarifLog
