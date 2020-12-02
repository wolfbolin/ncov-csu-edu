import Vue from 'vue';
import axios from 'axios';
import App from './App.vue';
import store from './store';
import router from './router';
import VueAxios from 'vue-axios';
import {
    Col,
    Row,
    Tag,
    Tabs,
    Form,
    Alert,
    Input,
    Table,
    Button,
    Slider,
    TabPane,
    Loading,
    FormItem,
    Message,
    Checkbox,
    Pagination,
    TimePicker,
    TableColumn,
    CheckboxGroup,
} from 'element-ui';

Vue.use(Col);
Vue.use(Row);
Vue.use(Tag);
Vue.use(Tabs);
Vue.use(Form);
Vue.use(Alert);
Vue.use(Input);
Vue.use(Table);
Vue.use(Button);
Vue.use(Slider);
Vue.use(TabPane);
Vue.use(Loading);
Vue.use(FormItem);
Vue.use(Checkbox);
Vue.use(Pagination);
Vue.use(TimePicker);
Vue.use(TableColumn);
Vue.use(CheckboxGroup);

Vue.use(VueAxios, axios);
Vue.config.productionTip = false;
Vue.prototype.$message = Message;

new Vue({
    router,
    store,
    render: (h) => h(App),
}).$mount('#app');
