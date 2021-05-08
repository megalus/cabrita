"""
Tests init sub-package.

This subpackage contain all unit tests.
This file contains mocked data from docker inspect command.
"""
LATEST_CONFIG_PATH = "./examples/config/cabrita-v2.yml"

INSPECT_DJANGO_CONTAINER = """
    [
        {
            "Id": "b075cee9bc12b262d99ff7068750acb3ac87ceadbffb0f4d040bb2f17521b7cc",
            "Created": "2018-05-15T19:01:45.368531178Z",
            "Path": "python",
            "Args": [
                "manage.py",
                "runserver",
                "0.0.0.0:8080"
            ],
            "State": {
                "Status": "running",
                "Running": true,
                "Paused": false,
                "Restarting": false,
                "OOMKilled": false,
                "Dead": false,
                "Pid": 12248,
                "ExitCode": 0,
                "Error": "",
                "StartedAt": "2018-05-15T19:01:46.001072029Z",
                "FinishedAt": "0001-01-01T00:00:00Z"
            },
            "Image": "sha256:f17b832c2c7e7449d763b8a7e78d1c95ce34f19fe75701f1314733d404809d5b",
            "ResolvConfPath": "/var/lib/docker/containers/b075cee9bc12b262d99ff7068750acb3ac87ceadbffb0f4d040bb2f17521b7cc/resolv.conf",
            "HostnamePath": "/var/lib/docker/containers/b075cee9bc12b262d99ff7068750acb3ac87ceadbffb0f4d040bb2f17521b7cc/hostname",
            "HostsPath": "/var/lib/docker/containers/b075cee9bc12b262d99ff7068750acb3ac87ceadbffb0f4d040bb2f17521b7cc/hosts",
            "LogPath": "/var/lib/docker/containers/b075cee9bc12b262d99ff7068750acb3ac87ceadbffb0f4d040bb2f17521b7cc/b075cee9bc12b262d99ff7068750acb3ac87ceadbffb0f4d040bb2f17521b7cc-json.log",
            "Name": "/examples_django_1",
            "RestartCount": 0,
            "Driver": "overlay2",
            "Platform": "linux",
            "MountLabel": "",
            "ProcessLabel": "",
            "AppArmorProfile": "docker-default",
            "ExecIDs": null,
            "HostConfig": {
                "Binds": [
                    "/home/chris/Documentos/Projetos/cabrita/examples/django_app:/opt/app:rw"
                ],
                "ContainerIDFile": "",
                "LogConfig": {
                    "Type": "json-file",
                    "Config": {}
                },
                "NetworkMode": "examples_backend",
                "PortBindings": {
                    "8080/tcp": [
                        {
                            "HostIp": "",
                            "HostPort": "8081"
                        },
                        {
                            "HostIp": "",
                            "HostPort": "8090"
                        }
                    ]
                },
                "RestartPolicy": {
                    "Name": "",
                    "MaximumRetryCount": 0
                },
                "AutoRemove": false,
                "VolumeDriver": "",
                "VolumesFrom": [],
                "CapAdd": null,
                "CapDrop": null,
                "Dns": null,
                "DnsOptions": null,
                "DnsSearch": null,
                "ExtraHosts": null,
                "GroupAdd": null,
                "IpcMode": "shareable",
                "Cgroup": "",
                "Links": null,
                "OomScoreAdj": 0,
                "PidMode": "",
                "Privileged": false,
                "PublishAllPorts": false,
                "ReadonlyRootfs": false,
                "SecurityOpt": null,
                "UTSMode": "",
                "UsernsMode": "",
                "ShmSize": 67108864,
                "Runtime": "runc",
                "ConsoleSize": [
                    0,
                    0
                ],
                "Isolation": "",
                "CpuShares": 0,
                "Memory": 0,
                "NanoCpus": 0,
                "CgroupParent": "",
                "BlkioWeight": 0,
                "BlkioWeightDevice": null,
                "BlkioDeviceReadBps": null,
                "BlkioDeviceWriteBps": null,
                "BlkioDeviceReadIOps": null,
                "BlkioDeviceWriteIOps": null,
                "CpuPeriod": 0,
                "CpuQuota": 0,
                "CpuRealtimePeriod": 0,
                "CpuRealtimeRuntime": 0,
                "CpusetCpus": "",
                "CpusetMems": "",
                "Devices": null,
                "DeviceCgroupRules": null,
                "DiskQuota": 0,
                "KernelMemory": 0,
                "MemoryReservation": 0,
                "MemorySwap": 0,
                "MemorySwappiness": null,
                "OomKillDisable": false,
                "PidsLimit": 0,
                "Ulimits": null,
                "CpuCount": 0,
                "CpuPercent": 0,
                "IOMaximumIOps": 0,
                "IOMaximumBandwidth": 0
            },
            "GraphDriver": {
                "Data": {
                    "LowerDir": "/var/lib/docker/overlay2/13dae0dd83e5fa6a5dee555fe4c8c48573bd0e18630f3093acf61fcd21129d33-init/diff:/var/lib/docker/overlay2/99a0d23a626a975216a604e85464f163cd824b202cadf6c89d125a5c2ca1525e/diff:/var/lib/docker/overlay2/7c106daf42f3177723116a06824402e089f1d4e8c1c2451543fdb2405d1d1484/diff:/var/lib/docker/overlay2/171f0ed9b09d85e83abfc6409ddd5d14d639aef11a958929e00a4040b73aa59b/diff:/var/lib/docker/overlay2/9436f1c7defb36f290ec3b2c32f0314c3021c7e8422b9f31d2723bc00297f430/diff:/var/lib/docker/overlay2/553335ef683932e29237d21f705f9a043c08c8c6dc1173db13a40459a34be5b4/diff:/var/lib/docker/overlay2/c8feee33aaea9178ab6b8a9a876e44a55ab5987eec00d7106e0d4d187a7ec4c0/diff:/var/lib/docker/overlay2/04826330f9d326041314d83b2e3f9f6c408471eebb9b0d909126a34efa506fec/diff:/var/lib/docker/overlay2/937841fdfbd725a4af29c9f1f2914f8593d61ff78227e27229f393e072b0ac76/diff:/var/lib/docker/overlay2/720b7dfb3caea7934826d0f42f7a6c7e3bf613e8d8235c347341390957582296/diff:/var/lib/docker/overlay2/4bae8954169a656e918f9e5fee3a95d34319be17a1e23898a1babca7d30dbda4/diff:/var/lib/docker/overlay2/8e66cc15e07910a993bccd78519dd8630d33a3833eb4e8bc6df2ba689e38104d/diff",
                    "MergedDir": "/var/lib/docker/overlay2/13dae0dd83e5fa6a5dee555fe4c8c48573bd0e18630f3093acf61fcd21129d33/merged",
                    "UpperDir": "/var/lib/docker/overlay2/13dae0dd83e5fa6a5dee555fe4c8c48573bd0e18630f3093acf61fcd21129d33/diff",
                    "WorkDir": "/var/lib/docker/overlay2/13dae0dd83e5fa6a5dee555fe4c8c48573bd0e18630f3093acf61fcd21129d33/work"
                },
                "Name": "overlay2"
            },
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": "/home/chris/Documentos/Projetos/cabrita/examples/django_app",
                    "Destination": "/opt/app",
                    "Mode": "rw",
                    "RW": true,
                    "Propagation": "rprivate"
                }
            ],
            "Config": {
                "Hostname": "b075cee9bc12",
                "Domainname": "",
                "User": "",
                "AttachStdin": false,
                "AttachStdout": false,
                "AttachStderr": false,
                "ExposedPorts": {
                    "8080/tcp": {}
                },
                "Tty": false,
                "OpenStdin": false,
                "StdinOnce": false,
                "Env": [
                    "DEBUG=True",
                    "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "LANG=C.UTF-8",
                    "GPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D",
                    "PYTHON_VERSION=3.6.5",
                    "PYTHON_PIP_VERSION=10.0.1"
                ],
                "Cmd": [
                    "python",
                    "manage.py",
                    "runserver",
                    "0.0.0.0:8080"
                ],
                "Image": "django:dev",
                "Volumes": {
                    "/opt/app": {}
                },
                "WorkingDir": "/opt/app",
                "Entrypoint": null,
                "OnBuild": null,
                "Labels": {
                    "com.docker.compose.config-hash": "74078fe2eb765fd5f6fe0ec17b3741f2278b04c722e63a0b953cface06e5e40e",
                    "com.docker.compose.container-number": "1",
                    "com.docker.compose.oneoff": "False",
                    "com.docker.compose.project": "examples",
                    "com.docker.compose.service": "django",
                    "com.docker.compose.version": "1.20.1"
                }
            },
            "NetworkSettings": {
                "Bridge": "",
                "SandboxID": "84f946c1466626ed08daab099a0674369c0e8ccd8ca2eddd17627f675a8e472f",
                "HairpinMode": false,
                "LinkLocalIPv6Address": "",
                "LinkLocalIPv6PrefixLen": 0,
                "Ports": {
                    "8080/tcp": [
                        {
                            "HostIp": "0.0.0.0",
                            "HostPort": "8090"
                        },
                        {
                            "HostIp": "0.0.0.0",
                            "HostPort": "8081"
                        }
                    ]
                },
                "SandboxKey": "/var/run/docker/netns/84f946c14666",
                "SecondaryIPAddresses": null,
                "SecondaryIPv6Addresses": null,
                "EndpointID": "",
                "Gateway": "",
                "GlobalIPv6Address": "",
                "GlobalIPv6PrefixLen": 0,
                "IPAddress": "",
                "IPPrefixLen": 0,
                "IPv6Gateway": "",
                "MacAddress": "",
                "Networks": {
                    "examples_backend": {
                        "IPAMConfig": null,
                        "Links": null,
                        "Aliases": [
                            "b075cee9bc12",
                            "django"
                        ],
                        "NetworkID": "36cb799765946fe41b07dfbdb38de404c86b38d46e67858ca730ce1ff9a3c123",
                        "EndpointID": "edeeb3ac1144cc0f811bd55a855b26bb89ef6eaaa1829c26f223df9a7ff16c44",
                        "Gateway": "172.21.0.1",
                        "IPAddress": "172.21.0.6",
                        "IPPrefixLen": 16,
                        "IPv6Gateway": "",
                        "GlobalIPv6Address": "",
                        "GlobalIPv6PrefixLen": 0,
                        "MacAddress": "02:42:ac:15:00:06",
                        "DriverOpts": null
                    }
                }
            }
        }
    ]
    """

INSPECT_DJANGO_IMAGE = """
    [
        {
            "Id": "sha256:f17b832c2c7e7449d763b8a7e78d1c95ce34f19fe75701f1314733d404809d5b",
            "RepoTags": [
                "django:dev"
            ],
            "RepoDigests": [],
            "Parent": "sha256:08064295e431e13152c267dbe43ed90464fc1e5526e82c973eeeea8fea99cd67",
            "Comment": "",
            "Created": "2018-05-15T15:53:56.199420064Z",
            "Container": "ddd14f04783b628d8444d20fa1f5d9823b726d58a538ad1cc5e92791220d8336",
            "ContainerConfig": {
                "Hostname": "ddd14f04783b",
                "Domainname": "",
                "User": "",
                "AttachStdin": false,
                "AttachStdout": false,
                "AttachStderr": false,
                "ExposedPorts": {
                    "8080/tcp": {}
                },
                "Tty": false,
                "OpenStdin": false,
                "StdinOnce": false,
                "Env": [
                    "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "LANG=C.UTF-8",
                    "GPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D",
                    "PYTHON_VERSION=3.6.5",
                    "PYTHON_PIP_VERSION=10.0.1"
                ],
                "Cmd": [
                    "/bin/sh",
                    "-c",
                    "#(nop) ",
                    "CMD ['python' 'manage.py' 'runserver' '0.0.0.0:8080']"
                ],
                "ArgsEscaped": true,
                "Image": "sha256:08064295e431e13152c267dbe43ed90464fc1e5526e82c973eeeea8fea99cd67",
                "Volumes": null,
                "WorkingDir": "/opt/app",
                "Entrypoint": null,
                "OnBuild": [],
                "Labels": {}
            },
            "DockerVersion": "18.05.0-ce",
            "Author": "",
            "Config": {
                "Hostname": "",
                "Domainname": "",
                "User": "",
                "AttachStdin": false,
                "AttachStdout": false,
                "AttachStderr": false,
                "ExposedPorts": {
                    "8080/tcp": {}
                },
                "Tty": false,
                "OpenStdin": false,
                "StdinOnce": false,
                "Env": [
                    "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                    "LANG=C.UTF-8",
                    "GPG_KEY=0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D",
                    "PYTHON_VERSION=3.6.5",
                    "PYTHON_PIP_VERSION=10.0.1"
                ],
                "Cmd": [
                    "python",
                    "manage.py",
                    "runserver",
                    "0.0.0.0:8080"
                ],
                "ArgsEscaped": true,
                "Image": "sha256:08064295e431e13152c267dbe43ed90464fc1e5526e82c973eeeea8fea99cd67",
                "Volumes": null,
                "WorkingDir": "/opt/app",
                "Entrypoint": null,
                "OnBuild": [],
                "Labels": null
            },
            "Architecture": "amd64",
            "Os": "linux",
            "Size": 774571267,
            "VirtualSize": 774571267,
            "GraphDriver": {
                "Data": {
                    "LowerDir": "/var/lib/docker/overlay2/7c106daf42f3177723116a06824402e089f1d4e8c1c2451543fdb2405d1d1484/diff:/var/lib/docker/overlay2/171f0ed9b09d85e83abfc6409ddd5d14d639aef11a958929e00a4040b73aa59b/diff:/var/lib/docker/overlay2/9436f1c7defb36f290ec3b2c32f0314c3021c7e8422b9f31d2723bc00297f430/diff:/var/lib/docker/overlay2/553335ef683932e29237d21f705f9a043c08c8c6dc1173db13a40459a34be5b4/diff:/var/lib/docker/overlay2/c8feee33aaea9178ab6b8a9a876e44a55ab5987eec00d7106e0d4d187a7ec4c0/diff:/var/lib/docker/overlay2/04826330f9d326041314d83b2e3f9f6c408471eebb9b0d909126a34efa506fec/diff:/var/lib/docker/overlay2/937841fdfbd725a4af29c9f1f2914f8593d61ff78227e27229f393e072b0ac76/diff:/var/lib/docker/overlay2/720b7dfb3caea7934826d0f42f7a6c7e3bf613e8d8235c347341390957582296/diff:/var/lib/docker/overlay2/4bae8954169a656e918f9e5fee3a95d34319be17a1e23898a1babca7d30dbda4/diff:/var/lib/docker/overlay2/8e66cc15e07910a993bccd78519dd8630d33a3833eb4e8bc6df2ba689e38104d/diff",
                    "MergedDir": "/var/lib/docker/overlay2/99a0d23a626a975216a604e85464f163cd824b202cadf6c89d125a5c2ca1525e/merged",
                    "UpperDir": "/var/lib/docker/overlay2/99a0d23a626a975216a604e85464f163cd824b202cadf6c89d125a5c2ca1525e/diff",
                    "WorkDir": "/var/lib/docker/overlay2/99a0d23a626a975216a604e85464f163cd824b202cadf6c89d125a5c2ca1525e/work"
                },
                "Name": "overlay2"
            },
            "RootFS": {
                "Type": "layers",
                "Layers": [
                    "sha256:2c833f307fd8f18a378b71d3c43c575fabdb88955a2198662938ac2a08a99928",
                    "sha256:3b65755e12206ea9db893a20d4cdba2bdff09d361386ebda0b823f025ce9449b",
                    "sha256:8b229ec781210796d4794168c1c765847effed18ddf032e66f011393562fdfb7",
                    "sha256:23044129c2ac1afdf93dadb7cabdacf73026d81fe6f659fbae47d5ce74628e26",
                    "sha256:7ad7ab2d38957d39d9c97557eed26f59f0c99bfcecfd6248eaccacaebf06c39d",
                    "sha256:b57c982f5768600c16265a52da743a7567514e5505777f7aa66de23c414153d9",
                    "sha256:ac0e7b8ba9e83f6bfbf8bb81ab0cab5138656f4e60ca1c577f7857747b737a51",
                    "sha256:0e4f7fa7eb0620da6b64a56de0c9be52b4404c0d0041a658bc9118a0832695d7",
                    "sha256:0ad25ada580438b1cce023174a35419e2c2d2fe52e5b02c7baecb12a509b14ca",
                    "sha256:c712305d7abed0de8fc5b564a0da4eecc720e34d6f4772cbd026b6dc075286cb",
                    "sha256:a909bf699dd540dbab0ae54d2f18eac02c607af87f62b2f1d9c48dd43419f86c"
                ]
            },
            "Metadata": {
                "LastTagTime": "2018-05-15T13:07:46.769658346-03:00"
            }
        }
    ]
    """
