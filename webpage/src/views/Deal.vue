<template>
    <div class="wb-deal">
        <div class="inner">
            <img src="@/assets/logo.png" class="logo" alt="logo"/>
            <h1>CSU-COVID19-SIGN</h1>
            <p>让我们一起建立更加深刻的契约吧</p>
            <div class="alert">
                <el-alert title="服务反馈与通知群 1158608406" type="warning" center :closable="false"></el-alert>
            </div>
            <div class="readme">
                <h2>功能说明</h2>
                <el-row :gutter="36">
                    <el-col :sm="12" :xs="24">
                        <h3>友情捐赠</h3>
                        <p>
                            本服务免费向用户提供，用于帮助用户完成每日签到打卡任务。
                        </p>
                        <p>
                            <span>与此同时，作者一直在支付高额的服务器相关费用。随着用户群体的不断增长，</span>
                            <span>服务更新和开发的压力也在不断增大，如果你不忍心看作者天天吃泡面，</span>
                            <span>可以通过下方的功能向他投食，能不能吃一顿九元的饺子就看各位老板了。</span>
                        </p>
                    </el-col>
                    <el-col :sm="12" :xs="24">
                        <h3>附加服务</h3>
                        <p>
                            <span>附加服务满足了部分用户的额外需求，</span>
                            <span>这些特殊功能的设计和使用，都消耗着额外的资源，</span>
                            <span>因此需要一些代价才能获得它们。</span>
                        </p>
                        <p>
                            <span>除捐助服务外，其他选项的费用由系统标定，有效期为一个月。</span>
                            <span>若在此期间发生服务变更，可向作者申请全额退还相关费用。</span>
                            <span>重复充值不能延迟有效期(还没写好代码)，请不要那么做。</span>
                        </p>
                    </el-col>
                </el-row>
                <el-row :gutter="36">
                    <el-col :sm="12" :xs="24">
                        <h3>短信提示</h3>
                        <p>
                            用户可以选择启用这项服务，帮助用户每日快速检查打卡的结果。
                        </p>
                        <p>
                            <span>如果您选用了这项服务，请确保您填写的手机号码为您个人的手机号，</span>
                            <span>并在手机短信联系相关的软件中，添加关键词 "Tinoy" (不含引号)</span>
                            <span>为白名单关键字，系统将在每日打卡操作结束后发送结果到您的手机。</span>
                            <span>若出现重复发送或提示打卡失败，请自行手动检查当日打卡结果。</span>
                        </p>
                    </el-col>
                    <el-col :sm="12" :xs="24">
                        <h3>随机时间</h3>
                        <p>
                            用户可以选择启用这项服务，帮助用户每天随机调整打卡的时间。
                        </p>
                        <p>
                            <span>如果您选用了这项服务，您可以在用户页面修改您每日打卡的时段，</span>
                            <span>系统将在次日的打卡过程中，为您在该时段内随机挑选一个时间点进行打卡，</span>
                            <span>如果您是对打卡时段有要求，或介意固定打卡时间的用户，建议您选择该功能。</span>
                        </p>
                    </el-col>
                </el-row>
            </div>
            <div class="panel">
                <el-tabs v-model="activeTab" type="card">
                    <el-tab-pane label="创建" name="create"></el-tab-pane>
                    <el-tab-pane label="查询" name="select"></el-tab-pane>
                </el-tabs>
            </div>
            <div class="order" v-if="activeTab === 'create'">
                <el-row :gutter="20" class="wb-alipay">
                    <el-col :xs="24" :sm="16">
                        <el-form :model="order" :rules="payRule" ref="payForm" label-width="80px"
                                 label-position="right" class="wb-alipay-form">
                            <el-form-item label="选择功能" style="text-align: left" prop="itemList">
                                <el-checkbox-group v-model="order.itemList" size="small" @change="choose_change">
                                    <template v-for="item in menu">
                                        <el-checkbox v-bind:key="item.name" :label="item.name"
                                                     class="wb-checkbox" border></el-checkbox>
                                    </template>
                                </el-checkbox-group>
                            </el-form-item>
                            <el-form-item label="捐助金额" prop="donation"
                                          v-if="order.itemList.indexOf('友情捐助') !== -1">
                                <el-slider v-model="order.donation" :min="1" :max="200"
                                           @change="choose_change" style="padding: 0 12px"></el-slider>
                            </el-form-item>
                            <el-form-item label="用户学号" prop="username">
                                <el-input type="text" v-model="order.username"></el-input>
                            </el-form-item>
                            <el-form-item label="手机号码" prop="phone">
                                <el-input type="text" v-model="order.phone"></el-input>
                            </el-form-item>
                            <el-form-item label="支付留言" prop="attach">
                                <el-input type="textarea" v-model="order.attach" maxlength="128"
                                          show-word-limit></el-input>
                            </el-form-item>
                            <div class="alert">
                                <el-alert title="请在支付完成后确认支付结果" type="info" center :closable="false"></el-alert>
                            </div>
                            <el-button @click="query_payment" v-if="order.order_status !== '未创建'">
                                刷新
                            </el-button>
                            <el-button type="primary" @click="precreat_payment" v-else>
                                提交
                            </el-button>
                        </el-form>
                    </el-col>
                    <el-col :xs="24" :sm="8" class="wb-alipay-qrcode">
                        <p>交易金额：{{ order.volume }}元(RMB)</p>
                        <img v-if="order.order_status === '未创建'"
                             src="@/assets/QR_Code.png" alt="qrcode"/>
                        <img v-else-if="order.order_status === '已支付'"
                             src="@/assets/done.png" alt="qrcode"/>
                        <div class="alert" v-if="order.order_status === '未创建'">
                            <el-alert title="请使用支付宝" type="info" center :closable="false"></el-alert>
                        </div>
                        <div v-else>
                            <vue-qr :text="order.order_link"></vue-qr>
                            <el-button type="primary" @click="open_app" plain>在支付宝中打开</el-button>
                        </div>
                        <p>状态：{{ order.order_status }}</p>
                        <p>订单号：{{ order.order_str }}</p>
                    </el-col>
                </el-row>
            </div>
            <div class="order" v-if="activeTab === 'select'">
                <el-form :model="order" :rules="payRule" ref="payForm" label-width="80px"
                         label-position="right" class="wb-alipay-form">
                    <el-form-item label="用户学号" prop="username">
                        <el-input type="text" v-model="order.username"></el-input>
                    </el-form-item>
                    <el-form-item label="手机号码" prop="phone">
                        <el-input type="text" v-model="order.phone"></el-input>
                    </el-form-item>
                    <el-button type="primary" @click="check_payment">
                        查询
                    </el-button>
                </el-form>
                <el-table class="table" v-loading="loading" :data="dataTable">
                    <el-table-column prop="id" label="订单"></el-table-column>
                    <el-table-column prop="item" label="服务">
                        <template slot-scope="scope">
                            <template v-for="item in scope.row.item">
                                <el-tag :key="item">{{ item }}</el-tag>
                            </template>
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态"></el-table-column>
                    <el-table-column prop="time" label="时间"></el-table-column>
                </el-table>
            </div>
            <div class="readme">
                <h2>友情赞助</h2>
                <div>
                    <template v-for="donor in donor_list">
                        <el-tag :key="donor">{{ donor }}</el-tag>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import vueQr from 'vue-qr'

export default {
    components: {vueQr},
    name: "Unbind",
    data() {
        let checkPhone = (rule, value, callback) => {
            if (!value) {
                return callback(new Error('请输入登录手机号'));
            } else {
                const reg = /^1[3|4|5|7|8][0-9]\d{8}$/
                if (reg.test(value)) {
                    return callback();
                } else {
                    return callback(new Error('请输入登录手机号'));
                }
            }
        };
        return {
            timer: null,
            loading: false,
            itemList: [],
            activeTab: "create",
            qrcode_image: "",
            order: {
                itemList: [],
                donation: 0,
                volume: 0,
                username: "",
                phone: "",
                attach: "",
                order_str: "Bill-xxxxxxxxx",
                order_link: "",
                order_status: "未创建",
            },
            menu: [],
            payRule: {
                itemList: [
                    {required: true, message: "至少选择一个吧", trigger: "change"}
                ],
                subject: [
                    {required: true, message: "请输入商品名称", trigger: "blur"},
                    {min: 3, max: 15, message: "3-15个字符哦", trigger: "blur"},
                ],
                donation: [
                    {required: true, message: "请输入捐助金额", trigger: "blur"},
                    {type: 'number', message: "这个数目不合适", min: 1, max: 200, trigger: "blur"}
                ],
                phone: [
                    {required: true, message: "请输入登录手机号", trigger: "blur"},
                    {validator: checkPhone, trigger: "blur"}
                ],
                username: [
                    {required: true, message: "请输入登录用户学号", trigger: "blur"},
                    {min: 6, max: 14, message: "请输入登录用户学号", trigger: "blur"},
                ],
                attach: [
                    {min: 0, max: 128, message: "太长了，太长了", trigger: "blur"},
                ]
            },
            dataTable: [],
            donor_list: []
        }
    },
    methods: {
        open_app: function () {
            window.open(this.order.order_link)
        },
        choose_change: function () {
            let volume = 0
            for (let choose of this.order.itemList) {
                for (let item of this.menu) {
                    if (item.name === choose) {
                        volume += item.volume
                        break
                    }
                }
            }
            if (this.order.itemList.indexOf('友情捐助') !== -1) {
                this.order.volume = volume + this.order.donation
            }else{
                this.order.volume = volume
            }
        },
        fetch_volume: function () {
            let that = this;
            let data_host = this.$store.state.host;
            let http_url = data_host + `/deal/menu`
            this.$http.get(http_url)
                .then(function (res) {
                    console.log(res.data)
                    if (res.data.status === "success") {
                        that.menu = res.data.data
                    }
                })
                .catch(function (res) {
                    console.log(res)
                })
        },
        fetch_donor: function () {
            let that = this;
            let data_host = this.$store.state.host;
            let http_url = data_host + `/user/donor`
            this.$http.get(http_url)
                .then(function (res) {
                    console.log(res.data)
                    if (res.data.status === "success") {
                        that.donor_list = res.data.data
                    }
                })
                .catch(function (res) {
                    console.log(res)
                })
        },
        precreat_payment: function () {
            this.$refs["payForm"].validate((valid) => {
                    if (valid) {
                        console.log("Creat deal order")
                        // 数据预处理
                        let itemList = []
                        for (let choose of this.order.itemList) {
                            for (let item of this.menu) {
                                if (item.name === choose) {
                                    itemList.push(item.key)
                                    break
                                }
                            }
                        }

                        // 创建交易订单
                        let that = this;
                        let data_host = this.$store.state.host;
                        let http_url = data_host + `/deal/order`
                        this.$http.post(http_url,
                            {
                                username: this.order.username,
                                phone: this.order.phone,
                                donation: this.order.donation,
                                attach: this.order.attach,
                                item_list: itemList,
                            })
                            .then(function (res) {
                                if (res.data.status === "success") {
                                    let order_info = res.data.data
                                    that.order.order_status = "已创建"
                                    that.order.order_str = order_info["order_str"]
                                    that.order.order_link = order_info["qrcode_link"]
                                    that.timer = setInterval(that.query_payment, 2000)
                                } else {
                                    that.$message({
                                        message: res.data.message,
                                        type: 'error'
                                    });
                                }
                            })
                            .catch(function (res) {
                                console.log(res)
                            })
                    }
                }
            )
        },
        query_payment: function () {
            console.log("Check deal order")
            let that = this;
            let data_host = this.$store.state.host;
            let http_url = data_host + `/deal/order`
            this.$http.get(http_url, {
                params: {
                    phone: this.order.phone,
                    username: this.order.username,
                    order_str: this.order.order_str,
                }
            })
                .then(function (res) {
                    if (res.data.status === "success") {
                        console.log(res.data)
                        switch (res.data.order_status) {
                            case "NOT_EXIST":
                                that.order.order_status = "未创建";
                                break;
                            case "CREATE":
                                that.order.order_status = "已创建";
                                break;
                            case "WAITING":
                                that.order.order_status = "待支付";
                                break;
                            case "SUCCESS":
                                that.order.order_status = "已支付";
                                break;
                            case "FINISH":
                                that.order.order_status = "已终止";
                                break;
                            case "CLOSE":
                                that.order.order_status = "已关闭";
                                break;
                            default:
                                that.order.order_status = "未知";
                        }
                        if (["已支付", "已终止", "已关闭"].indexOf(that.order.order_status) !== -1) {
                            clearInterval(that.timer)
                        }
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    console.log(res)
                })
        },
        check_payment: function () {
            console.log("Check deal order")
            let that = this
            this.loading = true
            let data_host = this.$store.state.host
            let http_url = data_host + `/deal/order/check`
            this.$http.get(http_url, {
                params: {
                    phone: this.order.phone,
                    username: this.order.username
                }
            })
                .then(function (res) {
                    that.loading = false
                    if (res.data.status === "success") {
                        console.log(res.data)
                        that.dataTable = res.data.data
                    } else {
                        that.$message({
                            message: res.data.message,
                            type: 'error'
                        });
                    }
                })
                .catch(function (res) {
                    that.loading = false
                    console.log(res)
                })
        }
    },
    mounted() {
        this.fetch_volume()
        this.fetch_donor()
    }
}
</script>

<style lang="scss" scoped>
.wb-deal {
    .panel {
        width: 90%;
        margin: 16px auto auto;
    }

    .order {
        width: 90%;
        margin-top: 32px;
        display: inline-block;

        .wb-checkbox {
            margin-right: 10px;
        }

        .wb-alipay-form {
            .el-button {
                width: 60%;
                margin-bottom: 36px;
            }
        }
    }

    .readme {
        .el-tag {
            height: 48px;
            padding: 0 20px;
            line-height: 48px;
            font-size: 16px;
            margin: 10px;
        }
    }
}
</style>