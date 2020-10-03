import Vue from 'vue';
import axios from 'axios';
import App from './App.vue';
import store from './store';
import router from './router';
import VueAxios from 'vue-axios';
import {
  Form,
  FormItem,
  Input,
  TimePicker,
  Button,
  Table,
  TableColumn,
} from 'element-ui';

Vue.use(Form);
Vue.use(FormItem);
Vue.use(Input);
Vue.use(TimePicker);
Vue.use(Button);
Vue.use(Table);
Vue.use(TableColumn);

Vue.use(VueAxios, axios);
Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app');
