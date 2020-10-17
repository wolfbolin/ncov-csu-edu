<template>
    <div id="app">
        <!-- 祖传导航栏 -->
        <header class="wb-nav">
            <div class="inner">
                <div class="float-left">
                    <p class="title">CSU-SIGN</p>
                </div>
                <div class="float-right">
                    <ul class="menu">
                        <li v-for="item in nav_list" :key="item.id" :class="item.class">
                            <a href="javascript:void(0);" v-on:click="switch_page(item.href)">{{ item.label }}</a>
                        </li>
                    </ul>
                </div>
            </div>
        </header>

        <!-- 页面内容 -->
        <div class="wb-view">
            <router-view/>
        </div>
        <!-- 祖传页脚 -->
        <footer class="wb-footer">
            <div class="inner">
                <p class="copyright" v-if="run_env==='desktop'">
                    CopyRight © 2020 WolfBolin.All Rights Reserved.
                </p>
                <p class="copyright" v-if="run_env==='phone'">
                    CopyRight © 2020 WolfBolin.<br/>All Rights Reserved.
                </p>
                <a href="http://www.miitbeian.gov.cn" class="icp">豫ICP备19033794号</a>
            </div>
        </footer>
    </div>
</template>

<script>
export default {
    name: 'app',
    data() {
        return {
            run_env: "desktop",
            logo_src: "",
            nav_list: [
                {"id": "index", "href": "/", "label": "主页", "class": ""},
                {"id": "list", "href": "/list", "label": "列表", "class": ""},
                {"id": "unbind", "href": "/unbind", "label": "解绑", "class": ""},
                {"id": "about", "href": "/about", "label": "关于", "class": ""},
            ],
        }
    },
    methods: {
        app_init: function () {
            console.log(
                `%c Designed by %c WolfBolin %c`,
                'background:#35495e ; padding: 1px; border-radius: 3px 0 0 3px;  color: #fff',
                'background:#41b883 ; padding: 1px; border-radius: 0 3px 3px 0;  color: #fff',
                'background:transparent'
            )
            console.log("Contact: mailto@wolfbolin.com");
            // 确定后台服务地址
            if (window.location.host.indexOf("localhost") !== -1) {
                this.$store.commit("setData", {key: "host", val: "http://127.0.0.1:12880/api"})
            } else if (window.location.host.indexOf("127.0.0.1") !== -1) {
                this.$store.commit("setData", {key: "host", val: "http://127.0.0.1:12880/api"})
            } else {
                this.$store.commit("setData", {key: "host", val: "https://covid19.csu-edu.cn/api"})
            }
            console.log("Server location:", this.$store.state.host);
            // 设置激活导航栏
            this.set_active_nav()
        },
        switch_page: function (path) {
            console.log("Switch page:", path);
            if (this.$route.path !== path) {
                this.$router.push(path);
            }
            this.set_active_nav()
        },
        set_active_nav: function () {
            let path_prefix = this.$route.path.split("/")[1];
            path_prefix = "/" + path_prefix;
            for (let item of this.nav_list) {
                if (path_prefix === item.href) {
                    item.class = 'active';
                } else {
                    item.class = '';
                }
            }
        }
    },
    watch: {
        '$route.path': function (to) {
            this.switch_page(to);
        }
    },
    created: function () {
        this.app_init();
    }
}
</script>

<style lang="scss">
html, body {
    margin: 0;
    padding: 0;
}

.inner {
    max-width: 1180px;
    margin: 0 auto;
}

.wb-nav {
    width: 100%;
    height: 64px;
    z-index: 100;
    position: fixed;
    font-weight: 200;
    background-color: white;

    .title {
        color: #3090e4;
        margin: 14px;
        font-weight: 400;
        font-size: 28px;
        line-height: 32px;
        text-decoration: none;
    }

    @media screen and (max-width:650px) {
        .title {
            margin: 14px 8px;
            font-size: 18px;
        }
    }



    .menu {
        margin: 0 1em;
        padding: 0;
    }

    .float-left {
        float: left;

        img {
            height: 40px;
            padding-top: 15px;
        }

        @media screen and (max-width: 768px) {
            img {
                padding: 15px 10px;
            }
        }
    }

    .float-right {
        float: right;

        .active {
            color: #91BEF0;
            border-bottom: 4px solid #91BEF0;
        }

        li {
            height: 60px;
            color: #3090e4;
            font-size: 18px;
            display: inline-block;
            text-align: -webkit-match-parent;
        }

        a {
            color: inherit;
            padding: 0 20px;
            line-height: 60px;
            text-decoration: none;
        }

        @media screen and (max-width: 768px) {
            a {
                padding: 0 5px;
            }
        }
    }


}

.wb-view {
    padding-top: 60px;
}

.wb-footer {
    margin-top: 72px;
    
    .copyright {
        margin: 0;
        color: #505050;
        padding: 10px;
        display: block;
        text-align: center;
    }

    .icp {
        margin: 0;
        color: #505050;
        display: block;
        text-align: center;
        padding-bottom: 5px;
    }
}
</style>
