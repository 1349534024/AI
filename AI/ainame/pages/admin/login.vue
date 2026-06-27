<template>
  <view class="container">
    <view class="panel">
      <view class="title">管理员登录</view>
      <view class="subtitle">运营与研发后台</view>
      <input class="input-box" v-model="form.email" placeholder="请输入管理员邮箱" />
      <input class="input-box" v-model="form.password" type="password" placeholder="请输入管理员密码" />
      <button class="btn" :loading="loading" @click="handleAdminLogin">进入后台</button>
      <view class="normal-link" @click="goUserLogin">返回普通用户登录</view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import http from '@/http/http.js';

const form = ref({
  email: '',
  password: ''
});
const loading = ref(false);

const handleAdminLogin = async () => {
  if (!form.value.email || !form.value.password) {
    return uni.showToast({ title: '请填写管理员账号和密码', icon: 'none' });
  }
  loading.value = true;
  try {
    const res = await http.adminLogin(form.value);
    uni.setStorageSync('token', res.token);
    uni.setStorageSync('user', res.user);
    uni.showToast({ title: '管理员登录成功', icon: 'success' });
    setTimeout(() => {
      uni.reLaunch({ url: '/pages/admin/users' });
    }, 600);
  } catch (error) {
    console.error('管理员登录失败', error);
  } finally {
    loading.value = false;
  }
};

const goUserLogin = () => {
  uni.redirectTo({ url: '/pages/login/login' });
};
</script>

<style scoped>
.container { min-height: 100vh; background: #f3f5f8; padding: 48rpx 36rpx; box-sizing: border-box; }
.panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 8rpx; padding: 44rpx 36rpx; box-sizing: border-box; }
.title { font-size: 44rpx; font-weight: bold; color: #111827; text-align: center; }
.subtitle { font-size: 26rpx; color: #667085; text-align: center; margin-top: 12rpx; margin-bottom: 56rpx; }
.input-box { border: 1px solid #d9e0e7; border-radius: 8rpx; padding: 22rpx 20rpx; margin-bottom: 24rpx; font-size: 28rpx; box-sizing: border-box; }
.btn { background: #18202f; color: #fff; margin-top: 32rpx; border-radius: 8rpx; }
.normal-link { text-align: center; color: #1677ff; margin-top: 30rpx; font-size: 26rpx; }
</style>
