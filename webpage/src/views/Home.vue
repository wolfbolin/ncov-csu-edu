<template>
    <div class="wb-home">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>简单几步即可建立羁绊</p>
            <div class="alert">
                <el-alert type="warning" center :closable="false">
                    <template slot="title">
                        服务反馈与通知群 {{ this.$store.state.group }}
                    </template>
                </el-alert>
            </div>
            <div class="readme">
                <h2>使用条款</h2>
                <el-row :gutter="36">
                    <el-col :sm="12" :xs="24">
                        <h3>关于打卡</h3>
                        <p>
                            <span>本服务用于向用户提供，每日签到打卡的自动检查能力。旨在帮助用户在容易遗忘的时刻也能保持打卡不中断。</span>
                            <span>这不代表你完全移交签到打卡的主动权，该服务仅作为减少工作量与提高效率的工具存在，</span>
                            <span>请自行衡量使用该服务所产生的影响，系统与用户可在任何时间主动终止服务。</span>
                        </p>
                        <p>
                            <span>本服务将在必要时调整面向使用者的用户政策，包含但不限于修改设置、暂停服务和移除账户。</span>
                        </p>
                    </el-col>
                    <el-col :sm="12" :xs="24">
                        <h3>数据安全</h3>
                        <p>
                            <span>本服务将不会在服务器中保存您的账号密码，这意味着如果本服务不慎丢失您的登录态，签到打卡服务将被暂停。</span>
                            <span>您可以在需要时解除绑定，当您成功解除绑定后，服务将清除您绑定时产生的登录信息，但将保留您其他的服务信息。</span>
                            <span>如果您有其他安全顾虑可以与开发者联系以获得帮助。</span>
                        </p>
                        <p>
                            <span>服务未与任何第三方组织和个人达成合作关系，未授权任何组织和个人代理完成打卡，谨防受骗。</span>
                        </p>
                    </el-col>
                </el-row>
                <el-row :gutter="36">
                    <el-col :sm="12" :xs="24">
                        <h3>使用说明</h3>
                        <p>
                            <span>本服务会通过代理访问的方式，验证您的账号信息并保留账号的登录态在数据库中。</span>
                            <span>为防止恶意使用代理，多次登录失败时将在一小时内的暂停登录服务。</span>
                        </p>
                        <p>
                            <span>系统不会也不能监控你的设备以实现数据的更新。</span>
                            <span>请自行保证打卡信息符合你个人的实际情况，请勿将打卡服务用于欺瞒、诈骗等手段。</span>
                        </p>

                    </el-col>
                    <el-col :sm="12" :xs="24">
                        <h3>常见问答</h3>
                        <p>
                            <span>本服务将在为您分配的时间点，使用您最后一次成功完成打卡的信息进行签到打卡。</span>
                            <span>当您的打卡信息需要变化时，请在服务自动打卡之前手动打卡一次，以实现打卡信息的更新。</span>
                        </p>
                        <p>
                            <span>系统将自动更新当前中高风险地区的疫情信息，并拒绝向中高风险地区所在城市提供打卡服务。</span>
                        </p>
                    </el-col>
                </el-row>
            </div>
            <div class="panel">
                <el-tabs v-model="activeTab" type="card">
                    <el-tab-pane label="绑定账号" name="bind">
                        <el-form class="form" ref="form1" label-position="left" label-width="60px"
                                 v-loading="loading" :rules="rules" :model="formData">
                            <el-form-item label="账号" prop="username">
                                <el-input v-model="formData.username" placeholder="信息门户账户"
                                          :disabled="closeOpen"></el-input>
                            </el-form-item>
                            <el-form-item label="手机" prop="phone">
                                <el-input v-model="formData.phone" placeholder="关联您的手机" type="number"
                                          :disabled="closeOpen"></el-input>
                            </el-form-item>
                            <el-form-item label="密码" prop="password">
                                <el-input v-model="formData.password" placeholder="信息门户密码"
                                          show-password :disabled="closeOpen"></el-input>
                            </el-form-item>
                            <el-form-item label="昵称" prop="nickname">
                                <el-input v-model="formData.nickname" placeholder="起个帅气昵称"
                                          :disabled="closeOpen"></el-input>
                            </el-form-item>
                            <el-form-item label="须知" prop="readme" style="text-align: left">
                                <el-checkbox v-model="formData.readme" :disabled="closeOpen">我已认真阅读并同意服务使用条款
                                </el-checkbox>
                            </el-form-item>
                            <div class="alert">
                                <el-alert :title="closeInfo" type="error" center
                                          v-if="closeOpen" :closable="false"></el-alert>
                            </div>
                            <div class="alert">
                                <el-alert type="warning">
                                    <template slot="title">
                                        <el-button type="text" @click="passwdTip=true">关于更新数据方法的说明</el-button>
                                    </template>
                                </el-alert>
                            </div>
                            <div class="alert">
                                <el-alert type="success">
                                    <router-link to="/deal">
                                        <el-button type="text" @click="passwdTip=true">短信通知、自定时间指路</el-button>
                                    </router-link>
                                </el-alert>
                            </div>
                            <el-button type="success" @click="check_form('add_task')" plain :disabled="closeOpen">
                                绑定账号
                            </el-button>
                        </el-form>
                    </el-tab-pane>
                    <el-tab-pane label="查询修改" name="modify">
                        <el-row>
                            <el-col :lg="16" :sm="16" :xs="24" class="info">
                                <el-form class="form" ref="form2" label-position="left" label-width="60px"
                                         v-loading="loading" :rules="rules" :model="formData">
                                    <el-form-item label="账号" prop="username">
                                        <el-input v-model="formData.username" placeholder="信息门户账户"></el-input>
                                    </el-form-item>
                                    <el-form-item label="手机" prop="phone">
                                        <el-input v-model="formData.phone" placeholder="用于身份认证"></el-input>
                                    </el-form-item>
                                    <el-form-item label="时间" prop="time" style="text-align: left">
                                        <el-select v-model="formData.time" placeholder="打卡时段"
                                                   :disabled="taskInfo.randOpt !== 'Yes'">
                                            <el-option v-for="item in taskTimeGroup" :key="item.value"
                                                       :label="item.label" :value="item.value">
                                            </el-option>
                                        </el-select>
                                    </el-form-item>
                                    <div class="alert">
                                        <el-alert type="success">仅限订阅了随机时间功能的用户修改打卡时段</el-alert>
                                    </div>
                                    <el-button type="primary" @click="check_form('mod_task')"
                                               plain v-if="taskInfo.randOpt === 'Yes'">修改任务
                                    </el-button>
                                    <el-button type="success" @click="check_form('get_task')" plain>查询状态</el-button>
                                </el-form>
                            </el-col>
                            <el-col :lg="8" :sm="8" :xs="24" class="info">
                                <el-row class="item">
                                    <el-col :span="12" class="key">
                                        <p>用户昵称</p>
                                    </el-col>
                                    <el-col :span="12" class="val">
                                        <p>{{ taskInfo.nickname }}</p>
                                    </el-col>
                                </el-row>
                                <el-row class="item">
                                    <el-col :span="12" class="key">
                                        <p>打卡时间</p>
                                    </el-col>
                                    <el-col :span="12" class="val">
                                        <p>{{ taskInfo.taskTime }}</p>
                                    </el-col>
                                </el-row>
                                <el-row class="item">
                                    <el-col :span="12" class="key">
                                        <p>随机时间</p>
                                    </el-col>
                                    <el-col :span="12" class="val">
                                        <p>{{ taskInfo.randOpt }}</p>
                                    </el-col>
                                </el-row>
                                <el-row class="item">
                                    <el-col :span="12" class="key">
                                        <p>短信通知</p>
                                    </el-col>
                                    <el-col :span="12" class="val">
                                        <p>{{ taskInfo.smsOpt }}</p>
                                    </el-col>
                                </el-row>
                            </el-col>
                        </el-row>
                    </el-tab-pane>
                    <el-tab-pane label="解除绑定" name="unbind">
                        <el-form class="form" ref="form3" label-position="left" label-width="60px"
                                 v-loading="loading" :rules="rules" :model="formData">
                            <el-form-item label="账号" prop="username">
                                <el-input v-model="formData.username" placeholder="信息门户账户"></el-input>
                            </el-form-item>
                            <el-form-item label="手机" prop="phone">
                                <el-input v-model="formData.phone" placeholder="用于身份认证"></el-input>
                            </el-form-item>
                            <div class="alert">
                                <el-alert type="warning">
                                    提交后立即生效，请勿重复提交
                                </el-alert>
                            </div>
                            <el-button type="danger" @click="check_form('del_task')" plain>解除绑定</el-button>
                        </el-form>
                    </el-tab-pane>
                </el-tabs>
            </div>
            <el-dialog title="验证码" :visible.sync="captcha.dialog" center>
                <p>请输入下图中的验证码(不可刷新)</p>
                <img :src="captcha.data" alt="captcha" style="vertical-align:middle"/>
                <el-input v-model="captcha.text" style="width: auto" maxlength="4"></el-input>
                <span slot="footer" class="dialog-footer">
                    <el-button @click="captcha.dialog = false">取 消</el-button>
                    <el-button type="primary" @click="user_login_captcha">确 定</el-button>
                </span>
            </el-dialog>

            <div class="tips">
                <h2>这是什么？</h2>
                <p>懂的都懂<br/>
                    不懂的我也不解释<br/>
                    这里水很深，利益牵扯太大<br/>
                    网上大部分内容都已经删除干净了<br/>
                    懂的人都是自己悟的<br/>
                    别不懂装懂<br/>
                    懂了吗<br/>
                </p>
                <h2>这安全吗？</h2>
                <p>不存储你的密码<br/>
                    服务使用SSL加密传输<br/>
                    仅在登录时使用账号密码<br/>
                    登录后打卡网站提供的Cookie<br/>
                    之后每一天都使用Cookie进行签到<br/>
                    Cookie无法用于获取其他信息<br/>
                    而且源码是开源的<br/>
                    接受安全反馈<br/>
                    <a href="https://github.com/wolfbolin/CSU-COVID19-SIGN" target="_blank">Github</a><br/>
                </p>
                <h2>以防万一</h2>
                <p>由于用户量增加<br/>
                    防止突如其来的服务中断<br/>
                    给你本来懒惰的打卡生活增添困扰<br/>
                    所以我建议你加入服务反馈群1158608406<br/>
                    如果出现业务内容的调整与变化<br/>
                    会尽快通知各位自行调整<br/>
                    @全体成员
                </p>
            </div>
            <el-dialog title="数据更新" width="80%" :visible.sync="passwdTip">
                <p>打卡服务会自动获取您前一日的打卡信息，作为打卡数据进行提交</p>
                <p>若您需要更新自己的打卡信息，可以在系统自动打卡之前手动打卡</p>
                <p>手动打卡数据不会被自动打卡数据覆盖，因此您无需频繁解除绑定</p>
                <p>目前已知基础信息、定位信息、疫苗信息均可以按照上述逻辑运行</p>
                <span slot="footer" class="dialog-footer">
                    <el-button type="primary" @click="passwdTip = false">确 定</el-button>
                </span>
            </el-dialog>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Home',
    data() {
        let checkReadme = (rule, value, callback) => {
            if (value) {
                return callback();
            } else {
                return callback("建立羁绊的必要前提");
            }
        };
        return {
            captcha: {
                dialog: false,
                data: "",
                text: ""
            },
            activeTab: "bind",
            loading: false,
            passwdTip: false,
            passwdAlert: false,
            closeInfo: "",
            closeOpen: false,
            formData: {
                username: "",
                password: "",
                nickname: "",
                readme: "",
                phone: "",
                time: ""
            },
            taskTimeGroup: [
                {value: "00", label: "00:00-00:59"},
                {value: "01", label: "01:00-01:59"},
                {value: "02", label: "02:00-02:59"},
                {value: "03", label: "03:00-03:59"},
                {value: "04", label: "04:00-04:59"},
                {value: "05", label: "05:00-05:59"},
                {value: "06", label: "06:00-06:59"},
                {value: "07", label: "07:00-07:59"},
                {value: "08", label: "08:00-08:59"},
                {value: "09", label: "09:00-09:59"},
            ],
            taskInfo: {
                nickname: "",
                taskTime: "",
                randOpt: "",
                smsOpt: ""
            },
            rules: {
                username: [
                    {required: true, message: '请输入信息门户账户', trigger: 'blur'},
                    {min: 6, max: 14, message: '长度在 6 到 14 个字符', trigger: 'blur'}
                ],
                password: [
                    {required: true, message: '请输入信息门户密码', trigger: 'blur'}
                ],
                nickname: [
                    {required: true, message: '给自己起个名字吧', trigger: 'blur'},
                    {min: 4, max: 16, message: '长度在 4 到 16 个字符', trigger: 'blur'}
                ],
                phone: [
                    {required: true, message: '请输入收信电话号码', trigger: 'blur'},
                    {min: 11, max: 11, message: '长度应为 11 个数字', trigger: 'blur'}
                ],
                readme: [
                    {required: true, validator: checkReadme, trigger: 'change'}
                ]
            }
        }
    },
    methods: {
        check_open: function () {
            this.loading = true;
            let that = this;
            let data_host = this.$store.state.host
            this.$http.get(data_host + `/open`)
                .then(function (res) {
                    that.loading = false;
                    if (res.data.status !== 'success') {
                        that.closeOpen = true
                        that.closeInfo = res.data.message
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                })
        },
        check_form: function (task) {
            if (task === "add_task") {
                this.$refs["form1"].validate((valid) => {
                    if (valid) {
                        this.user_login();
                    }
                })
            } else if (task === "get_task") {
                this.$refs["form2"].validate((valid) => {
                    if (valid) {
                        this.user_task();
                    }
                })
            } else if (task === "mod_task") {
                this.$refs["form2"].validate((valid) => {
                    if (valid) {
                        this.user_modify();
                    }
                })
            } else if (task === "del_task") {
                this.$refs["form3"].validate((valid) => {
                    if (valid) {
                        this.user_logout();
                    }
                })
            }
        },
        user_login: function () {
            let that = this;
            this.loading = true;
            let data_host = this.$store.state.host;
            let http_data = {
                username: this.formData.username,
                password: this.formData.password,
                nickname: this.formData.nickname,
                phone: this.formData.phone
            }
            this.$http.post(data_host + `/user/login`, http_data)
                .then(function (res) {
                    that.loading = false;
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.$message({
                            message: res.data.message,
                            type: 'success'
                        });
                        that.formData.password = ""
                    } else if (res.data.status === 'waiting') {
                        that.loading = false;
                        that.$message({
                            message: res.data.message,
                            type: 'warning'
                        });
                        that.captcha.text = ""
                        that.captcha.data = "data:image/jpg;base64," + res.data["captcha"]
                        that.captcha.session = res.data["login_data"]
                        that.captcha.dialog = true
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                    that.$message({
                        message: "网络异常，请重试",
                        type: 'error'
                    });
                })
        },
        user_login_captcha: function () {
            let that = this;
            this.loading = true;
            this.captcha.dialog = false;
            let data_host = this.$store.state.host;
            let http_data = {
                username: this.formData.username,
                password: this.formData.password,
                nickname: this.formData.nickname,
                phone: this.formData.phone,
                login_data: {
                    session: this.captcha.session,
                    captcha: this.captcha.text
                }
            }
            this.$http.post(data_host + `/user/login/captcha`, http_data)
                .then(function (res) {
                    that.loading = false;
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.$message({
                            message: res.data.message,
                            type: 'success'
                        });
                        that.formData.password = ""
                    } else if (res.data.status === 'waiting') {
                        that.loading = false;
                        that.$message({
                            message: res.data.message,
                            type: 'warning'
                        });
                        that.captcha.text = ""
                        that.captcha.data = "data:image/jpg;base64," + res.data["captcha"]
                        that.captcha.session = res.data["login_data"]
                        that.captcha.dialog = true
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                    that.$message({
                        message: "网络异常，请重试",
                        type: 'error'
                    });
                })
        },
        user_task: function () {
            let that = this;
            this.loading = true;
            let data_host = this.$store.state.host;
            this.$http.get(data_host + `/user/task`,
                {
                    params: {
                        username: this.formData.username,
                        phone: this.formData.phone,
                    }
                })
                .then(function (res) {
                    that.loading = false
                    if (res.data.status === "success") {
                        that.taskInfo = res.data.data
                        that.formData.time = that.taskInfo["taskTime"].split(":")[0]
                        if (that.taskInfo.randOpt === 'Yes') {
                            that.taskInfo.taskTime = "时段随机"
                        }
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                    that.$message({
                        message: "网络异常，请重试",
                        type: 'error'
                    });
                })
        },
        user_logout: function () {
            let that = this;
            this.loading = true;
            let data_host = this.$store.state.host;
            let http_data = {
                username: this.formData.username,
                phone: this.formData.phone,
            }
            this.$http.post(data_host + `/user/logout`, http_data)
                .then(function (res) {
                    that.loading = false;
                    if (res.data.status === 'success') {
                        that.loading = false;
                        that.$message({
                            message: res.data.message,
                            type: 'success'
                        });
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                    that.$message({
                        message: "网络异常，请重试",
                        type: 'error'
                    });
                })
        },
        user_modify: function () {
            let that = this;
            this.loading = true;
            let data_host = this.$store.state.host;
            let http_data = {
                username: this.formData.username,
                phone: this.formData.phone,
                time: this.formData.time
            }
            this.$http.put(data_host + `/user/task`, http_data)
                .then(function (res) {
                    that.loading = false
                    if (res.data.status === "success") {
                        that.$message({
                            message: res.data.message,
                            type: 'success'
                        });
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false;
                    console.log(res);
                    that.$message({
                        message: "网络异常，请重试",
                        type: 'error'
                    });
                })
        }
    },
    mounted() {
        this.check_open()
    }
}
</script>

<style lang="scss" scoped>
.wb-home {
    .panel {
        width: 90%;
        margin: 16px auto auto;
    }

    .form {
        width: 100%;
        margin-top: 16px;
        display: inline-block;
        text-align: center;

        .alert {
            .el-button {
                padding: 0;
            }
        }
    }

    .info {
        padding: 16px 16px;

        .item {
            margin-bottom: 12px;

            p {
                margin: 0.5em 0;
            }

            .key {
                min-height: 38px;
                border-radius: 4px;
                background-color: rgba(145, 190, 240, 0.3);
            }

            .val {
                min-height: 38px;
                background-color: rgba(145, 190, 240, 0.1);
            }
        }
    }

    .el-date-editor.el-input {
        width: 100%;
    }
}

</style>
