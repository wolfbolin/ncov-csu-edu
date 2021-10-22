import Vue from 'vue';
import axios from 'axios';
import App from './App.vue';
import store from './store';
import router from './router';
import VueAxios from 'vue-axios';
import VueCookies from 'vue-cookies';
import './assets/icon/version_icon/iconfont.css'

import {
    Col,
    Row,
    Tag,
    Tabs,
    Form,
    Alert,
    Input,
    Table,
    Dialog,
    Button,
    Slider,
    Select,
    Option,
    TabPane,
    Loading,
    FormItem,
    Message,
    Checkbox,
    Pagination,
    TimePicker,
    TableColumn,
    CheckboxGroup,
    Dropdown,
    DropdownItem,
    DropdownMenu,
    Icon,
} from 'element-ui';

Vue.use(Col);
Vue.use(Row);
Vue.use(Tag);
Vue.use(Tabs);
Vue.use(Form);
Vue.use(Alert);
Vue.use(Input);
Vue.use(Table);
Vue.use(Dialog);
Vue.use(Button);
Vue.use(Slider);
Vue.use(Select);
Vue.use(Option);
Vue.use(TabPane);
Vue.use(Loading);
Vue.use(FormItem);
Vue.use(Checkbox);
Vue.use(Pagination);
Vue.use(TimePicker);
Vue.use(TableColumn);
Vue.use(CheckboxGroup);
Vue.use(Dropdown);
Vue.use(DropdownMenu);
Vue.use(DropdownItem);
Vue.use(Icon);

Vue.use(VueAxios, axios);
Vue.use(VueCookies)
Vue.config.productionTip = false;
Vue.prototype.$message = Message;

new Vue({
    router,
    store,
    render: (h) => h(App),
}).$mount('#app');
