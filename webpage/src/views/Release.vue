<template>
    <div class="wb-changeLog">
        <div class="inner">
            <div class="release-nav">
                <img src="../assets/logo.png" class="logo" alt="logo"/>
                <div class="release-nav-intro">
                    <span>服务更新日志</span>
                    <el-alert :closable="false" type="info" center show-icon>
                        <template slot="title">
                            服务反馈与通知群 {{ this.$store.state.group }}
                        </template>
                    </el-alert>
                </div>
            </div>

            <div class="notice-board">
                <h2 class="title">服务公告</h2>
                <p> 当前版本: <span> {{ latestVersion }} </span></p>
                <p>{{ noticeData["intro"] }}</p>
            </div>

            <div class="release-list">
                <h2 class="release-label">Releases</h2>
                <template v-for="(item, index) in changeLogData">
                    <div class="release-entry" :key="item.version">
                        <div class="entry-left">
                            <div class="entry-text">
                                <el-tag>Version <span>{{ item.version }}</span></el-tag>
                            </div>
                        </div>

                        <div class="entry-right">
                            <div class="release-record">
                                <p>Release</p>
                                <span>Release at {{ timeStamp2date(item.date) }}</span>
                            </div>
                            <div class="release-info">
                                <template v-for="key in changeLabel">
                                    <div class="info-entry" :key="key" v-if="item[key].length !== 0">
                                        <span>{{ key.replace(/^\S/, s => s.toUpperCase()) }}</span>
                                        <ul>
                                            <li v-for="content in item[key]" :key="content">{{ content }}</li>
                                        </ul>
                                    </div>
                                </template>
                            </div>
                            <div class="user-reaction">
                                <div class="react-menu">
                                    <template v-for="btn in buttonType">
                                        <el-button class="react-item" :icon="btn.icon" type="primary"
                                                   @click="isButtonClicked(item.version, btn.type, index)"
                                                   :key="btn.type" v-if="item[btn.type]"
                                                   :disabled="isButtonDisable(item.version, btn.type)">
                                            {{ item[btn.type] }}
                                        </el-button>
                                    </template>
                                </div>
                                <el-dropdown trigger="click" @command="isDPitemClicked">
                                    <span class="sim-dropdown-link">
                                        <i class="fontFamily sim-icon-emoji"/>
                                    </span>
                                    <el-dropdown-menu slot="dropdown">
                                        <el-dropdown-item :command="`${item.version}-${btn.type}-${index}`"
                                                          v-for="btn in buttonType" :key="btn.type">
                                            <i :class="btn.icon"></i>
                                        </el-dropdown-item>
                                    </el-dropdown-menu>
                                </el-dropdown>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "Release",
    data() {
        return {
            buttonType: [
                {"type": "love", "icon": "fontFamily sim-icon-love"},
                {"type": "like", "icon": "fontFamily sim-icon-like"},
                {"type": "star", "icon": "fontFamily sim-icon-star"},
                {"type": "hate", "icon": "fontFamily sim-icon-hate"},
            ],
            noticeData: {
                version: "1.0.0",
                intro: ""
            },
            latestVersion: "",
            changeLabel: ["feature", "update", "bugfix"],
            changeLogData: [],
        }
    },
    methods: {
        isDPitemClicked(command) {
            // console.log(command)
            let cmd = command.split("-")
            this.isButtonClicked(cmd[0], cmd[1], cmd[2])
        },
        isButtonClicked(version, type, index) {
            // console.log(type, version, index)
            if (this.isButtonDisable(version, type)) {
                return
            }

            // TODO post data
            let that = this
            let data_host = this.$store.state.host
            this.$http.post(data_host + `/data/version/${version}/action/${type}`)
                .then(function (response) {
                    if (response.data.status === "success") {
                        that.$message({
                            message: response.data.message,
                            type: 'success'
                        });
                    } else {
                        that.$message({
                            message: response.data.message,
                            type: 'warning'
                        });
                    }
                })
                .catch(function (error) {
                    console.log(error)
                    that.$message("无法连接到服务器!")
                })


            this.$cookies.set(`${type}-${version}`, 1)
            this.changeLogData[index][type] += 1
        },
        isButtonDisable: function (version, type) {
            return this.$cookies.isKey(type + "-" + version);

        },
        timeStamp2date(timestamp) {
            let date = new Date(timestamp * 1000)
            let Y = date.getFullYear() + '-'
            let M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-'
            let D = date.getDate() + ' '
            return Y + M + D
        },
        getChangeLogData: function () {
            let that = this
            let data_host = this.$store.state.host
            this.$http.get(data_host + '/data/version')
                .then(function (response) {
                    //按照id降序排列
                    let listOfChangLog = Array.from(response.data, x => x)
                    listOfChangLog = listOfChangLog.sort(function (a, b) {
                        return b.id - a.id
                    })
                    // console.log(listOfChangLog)
                    that.changeLogData = listOfChangLog
                    that.latestVersion = listOfChangLog[0]["version"]
                })
                .catch(function (error) {
                    console.log(error)
                    that.$message("无法连接到服务器!")
                })
        },
        getNoticeData: function () {
            let that = this
            let data_host = this.$store.state.host
            this.$http.get(data_host + '/data/notice')
                .then(function (response) {
                    if (response.data.status === 'success') {
                        that.noticeData.intro = response.data.message
                    } else {
                        that.$message({
                            message: response.data.message,
                            type: 'warning'
                        });
                    }
                })
                .catch(function (error) {
                    console.log(error)
                    that.$message("无法连接到服务器!")
                })
        }
    },
    mounted() {
        this.getChangeLogData()
        this.getNoticeData()
    }
}
</script>


<style lang="scss" scoped>
.el-dropdown-menu {
    display: flex;
    flex-direction: row;
    padding: 0;

    .el-dropdown-menu__item {
        font-size: 20px;
        padding: 0 10px;

        i {
            margin: 0;
        }
    }
}

.wb-changeLog {
    min-width: 640px;

    .release-nav {
        margin: 64px auto;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;

        img {
            width: 120px;
            height: 120px;
            margin: 0;
            padding-right: 35px;
        }

        .release-nav-intro {
            display: flex;
            width: 250px;
            flex-direction: column;
            justify-content: flex-end;
            text-align: left;

            span {
                font-size: 24px;
                color: #3090e4;
                font-weight: 500;
                margin-bottom: 8px;
            }
        }
    }

    .notice-board {
        padding: 3rem;
        margin: 16px auto;
        text-align: left;
        border: 1px solid #dee2e6;
        background-color: #f8f8ff;

        .title {
            margin-top: 0;
            margin-bottom: 1rem;
            font-size: 2rem;
            font-weight: 500;
            line-height: 1.2;
            color: #3090e4;
        }

        span {
            font-weight: bold;
        }

        p {
            margin-top: 0;
            font-size: 1rem;
            margin-bottom: 1rem;
        }

    }


    .release-list {
        display: flex;
        flex-direction: column;

        .release-label {
            display: flex;
            align-self: flex-start;
            font-weight: 400;
            color: #3090e4;
        }

        .release-entry {
            display: flex;
            flex-direction: row;

            .entry-left {
                width: 15%;
                border-right: 1px solid lightgray;
                padding: 20px 20px 0 0;

                .entry-text {
                    float: right;
                }
            }

            .entry-right {
                width: 85%;
                padding: 20px 0 0 30px;

                .release-record {
                    text-align: left;
                    margin: 0;

                    p {
                        text-decoration: none;
                        font-size: 25px;
                        font-weight: 500;
                        color: #3090e4;
                        margin: 0;
                    }

                    span {
                        font-size: 15px;
                        font-weight: 400;
                        color: #565e64;
                    }
                }

                .release-info {
                    margin: 16px 0;
                    display: flex;
                    flex-direction: column;

                    .info-entry {
                        span {
                            display: block;
                            text-align: left;
                            font-weight: bold;
                            color: #565e64;
                            margin: 0;
                        }

                        ul {
                            margin: 8px 0;

                            li {
                                text-align: left;
                                font-size: 15px;
                                font-weight: 400;
                                color: #565e64;
                            }
                        }
                    }

                }

                .user-reaction {
                    display: flex;
                    padding: 0.3rem;
                    flex-direction: row-reverse;
                    justify-content: flex-end;
                    border-top: 1px solid lightgray;
                    border-bottom: 1px solid lightgray;
                    margin-bottom: 16px;

                    .react-menu {
                        margin: 0 10px;
                        display: flex;
                        flex-direction: row;

                        .react-item {
                            border-radius: 12px;
                            border: none;
                            background-color: #f0f0f0;
                            padding: 4px 12px;
                            margin: 3px 10px;
                            font-size: 16px;
                            color: #565e64;
                        }
                    }

                    .react-item:hover {
                        background-color: lightgray;
                    }

                    .sim-dropdown-link {
                        i {
                            font-size: 20px;
                        }
                    }

                    .el-dropdown {
                        margin: 5px 0;

                        span {
                            font-size: 16px;
                        }
                    }
                }
            }
        }
    }
}


</style>