<script setup>
import { onShow } from '@dcloudio/uni-app';

onShow(() => {
  const publicPages = ['pages/login/login', 'pages/register/register', 'pages/admin/login'];
  const token = uni.getStorageSync('token');
  const pages = getCurrentPages();
  const currentPage = pages.length ? pages[pages.length - 1].route : '';
  if (!token && currentPage && !publicPages.includes(currentPage)) {
    uni.reLaunch({ url: '/pages/login/login' });
  }
});
</script>

<style>
/* 每个页面公共css，这里暂不填 */
</style>
