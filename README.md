# 42Crunch-public-cli

## Installation

### Development

```bash
pip install poetry
poetry shell
poetry install
```

### Production

```bash
pip install --index https://$USERNAME:$PASSWORD@repo.42crunch.com/pypi/simple 42c-cli
```

## Api builder commands


### Authentication
#### Login
Login into Horus dashboard.
```bash
42c api-discover login
```
Options:
| Parameter     |        Default        |     Description     |
|:---------:    |:---------------------:|:-------------------:|
| -u, --url     | http://localhost:8080 | Horus dashboard url |
| -b, --browser | False | Open browser to login |

### Buckets
#### List buckets
Displays a list of all buckets of the user.
```bash
42c api-discover bucket list
```
#### Create bucket
Creates a new bucket.
```bash
42c api-discover bucket create <bucket_name> <bucket_host>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| bucket_name | Bucket name |
| bucket_host | Bucket host |

Options:
| Parameter     |        Default        |     Description     |
|:---------:    |:---------------------:|:-------------------:|
| -d, --description     | None | Bucket description |
| -b, --base-path | /* | Bucket base path |
| -h, --http | False | Enable http |
| -s, --https | True | Enable https |


#### get bucket
Displays a bucket.
```bash
42c api-discover bucket get <bucket_id>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| bucket_id | Bucket id |

#### Delete bucket
Deletes a bucket.
```bash
42c api-discover bucket delete <bucket_id>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| bucket_id | Bucket id |

#### Upload file
Uploads a file to a bucket (har, pcap, postman, etc).
```bash
42c api-discover bucket upload-file <bucket_id> <file_path>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| bucket_id | Bucket id |
| file_path | File path |

### Generation rules
#### List generation rules
Displays a list of all generation rules of a bucket.
```bash
42c api-discover generation-rule list <bucket_id>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| bucket_id | Bucket id |

#### get generation rule
Displays a generation rule.
```bash
42c api-discover generation-rule get <generation_rule_id>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| generation_rule_id | Generation rule id |

#### delete generation rule
Deletes a generation rule.
```bash
42c api-discover generation-rule delete <generation_rule_id>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| generation_rule_id | Generation rule id |

### QuickGen
#### Create QuickGen
Creates a new QuickGen and return an openapi.
```bash
42c api-discover quickgen create <config_file_path> <input_file_1> <input_file_2> ...
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| config_file_path | Config file path |
| input_file_1 | Input file path |
| input_file_2 | Input file path |

(At least one input file must be provided to create a QuickGen)

Options:
| Parameter     |        Default        |     Description     |
|:---------:    |:---------------------:|:-------------------:|
| -o, --output-file     | None | Output file path |
#### Create template
Creates a new QuickGen template to use in the creation of a QuickGen.
```bash
42c api-discover quickgen create-template
```

#### Recover last QuickGen
Recovers the last QuickGen created.
```bash
42c api-discover quickgen get
```

#### Save QuickGen
Save the current QuickGen as a normal bucket and generation rule projects.
```bash
42c api-discover quickgen save <bucket_name> <rule_name>
```
Arguments:
| Parameter |     Description     |
|:---------:|:-------------------:|
| bucket_name | Bucket name |
| rule_name | Generation rule name |

#### Delete QuickGen
Deletes the current QuickGen project.
```bash
42c api-discover quickgen delete
```
#### Recover Quickgen openapi
Recovers the openapi of the current QuickGen project.
```bash
42c api-discover quickgen get-openapi
```
Options:
| Parameter     |        Default        |     Description     |
|:---------:    |:---------------------:|:-------------------:|
| -o, --output-file     | None | Output file path |

### HTTP/HTTPS Proxy

#### Install proxy
As the proxy has a large number of dependencies, it is not installed by default. To install it, run the following commands:

For development:
```bash
poetry install -E proxy
```

For production:
```bash
pip install --index https://$USERNAME:$PASSWORD@repo.42crunch.com/pypi/simple 42c-cli[proxy]
```

#### Start proxy
Starts the proxy, use ctrl+c to stop it. Once stopped a har file will be generated in the current directory.
```bash
42c api-discover proxy start
```
Options:
| Parameter     |        Default        |     Description     |
|:---------:    |:---------------------:|:-------------------:|
| -p, --port     | 9999 | Proxy port |