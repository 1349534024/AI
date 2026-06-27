<template>
  <view class="page">
    <view class="admin-topbar">
      <view>
        <view class="admin-title">用户管理</view>
        <view class="admin-user">{{ currentUser.username || '管理员' }} {{ currentUser.email ? `/${currentUser.email}` : '' }}</view>
      </view>
      <button size="mini" class="logout-btn" @click="logoutAdmin">退出账号</button>
    </view>

    <view class="toolbar">
      <input class="search-input" v-model="keyword" placeholder="搜索邮箱或用户名" confirm-type="search" @confirm="refreshUsers" />
      <button class="search-btn" size="mini" @click="refreshUsers">搜索</button>
    </view>

    <view class="filters">
      <view :class="['filter-item', statusFilter === '' ? 'active' : '']" @click="changeStatus('')">全部({{ stats.total }})</view>
      <view :class="['filter-item', statusFilter === 'true' ? 'active' : '']" @click="changeStatus('true')">正常({{ stats.active }})</view>
      <view :class="['filter-item', statusFilter === 'false' ? 'active' : '']" @click="changeStatus('false')">冻结({{ stats.frozen }})</view>
    </view>

    <view class="summary">
      <text>共 {{ total }} 个用户</text>
      <text>第 {{ page }} 页</text>
    </view>

    <view v-if="loading" class="empty">加载中...</view>
    <view v-else-if="loadError" class="empty error-text">{{ loadError }}</view>
    <view v-else-if="users.length === 0" class="empty">暂无用户</view>

    <view class="user-card" v-for="item in users" :key="item.id">
      <view class="user-main">
        <view>
          <view class="username">{{ item.username }}</view>
          <view class="email">{{ item.email }}</view>
        </view>
        <view class="badges">
          <text v-if="item.is_admin" class="badge admin">管理员</text>
          <text :class="['badge', item.is_active ? 'active-badge' : 'frozen-badge']">
            {{ item.is_active ? '正常' : '冻结' }}
          </text>
        </view>
      </view>

      <view class="actions">
        <button size="mini" @click="openEdit(item)">修改</button>
        <button size="mini" @click="openReset(item)">重置密码</button>
        <button v-if="item.is_active" size="mini" class="warn-btn" @click="freezeUser(item)">冻结</button>
        <button v-else size="mini" class="ok-btn" @click="unfreezeUser(item)">解冻</button>
        <button size="mini" class="danger-btn" @click="deleteUser(item)">删除</button>
      </view>
    </view>

    <view class="pager" v-if="total > pageSize">
      <button size="mini" :disabled="page <= 1" @click="prevPage">上一页</button>
      <button size="mini" :disabled="page * pageSize >= total" @click="nextPage">下一页</button>
    </view>

    <view class="modal-mask" v-if="editing">
      <view class="modal">
        <view class="modal-title">修改用户</view>
        <input class="modal-input" v-model="editForm.username" placeholder="用户名" />
        <input class="modal-input" v-model="editForm.email" placeholder="邮箱" />
        <view class="switch-row">
          <text>管理员</text>
          <switch :checked="editForm.is_admin" @change="e => editForm.is_admin = e.detail.value" />
        </view>
        <view class="switch-row">
          <text>账号正常</text>
          <switch :checked="editForm.is_active" @change="e => editForm.is_active = e.detail.value" />
        </view>
        <view class="modal-actions">
          <button size="mini" @click="closeEdit">取消</button>
          <button size="mini" class="primary-btn" :loading="saving" @click="saveEdit">保存</button>
        </view>
      </view>
    </view>

    <view class="modal-mask" v-if="resetting">
      <view class="modal">
        <view class="modal-title">重置密码</view>
        <view class="target-user">{{ resetTarget.username }} / {{ resetTarget.email }}</view>
        <input class="modal-input" v-model="newPassword" type="password" placeholder="请输入新密码，至少4位" />
        <view class="modal-actions">
          <button size="mini" @click="closeReset">取消</button>
          <button size="mini" class="primary-btn" :loading="saving" @click="savePassword">确认重置</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';
import { onLoad, onPullDownRefresh } from '@dcloudio/uni-app';
import http from '@/http/http.js';

const users = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const keyword = ref('');
const statusFilter = ref('');
const loading = ref(false);
const saving = ref(false);
const loadError = ref('');
const currentUser = ref(uni.getStorageSync('user') || {});
const stats = ref({
  total: 0,
  active: 0,
  frozen: 0
});

const editing = ref(false);
const editTarget = ref({});
const editForm = ref({
  username: '',
  email: '',
  is_admin: false,
  is_active: true
});

const resetting = ref(false);
const resetTarget = ref({});
const newPassword = ref('');

const ensureAdmin = () => {
  const user = uni.getStorageSync('user') || {};
  currentUser.value = user;
  if (!user.is_admin) {
    uni.showToast({ title: '需要管理员权限', icon: 'none' });
    setTimeout(() => uni.reLaunch({ url: '/pages/admin/login' }), 800);
    return false;
  }
  return true;
};

const logoutAdmin = () => {
  uni.showModal({
    title: '退出账号',
    content: '退出当前管理员账号并返回管理员登录页？',
    success: (res) => {
      if (res.confirm) {
        http.logout('/pages/admin/login');
      }
    }
  });
};

const loadUsers = async () => {
  loading.value = true;
  loadError.value = '';
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value.trim()
    };
    if (statusFilter.value !== '') {
      params.is_active = statusFilter.value;
    }
    const res = await http.getAdminUsers(params);
    users.value = res.items || [];
    total.value = res.total || 0;
  } catch (error) {
    users.value = [];
    total.value = 0;
    loadError.value = '用户列表加载失败，请确认已用管理员账号登录并重启后端服务';
    console.error('用户列表加载失败', error);
  } finally {
    loading.value = false;
    uni.stopPullDownRefresh();
  }
};

const loadStats = async () => {
  try {
    const res = await http.getAdminUserStats({
      keyword: keyword.value.trim()
    });
    stats.value = {
      total: res.total || 0,
      active: res.active || 0,
      frozen: res.frozen || 0
    };
  } catch (error) {
    console.error('用户统计加载失败', error);
  }
};

const refreshUsers = () => {
  page.value = 1;
  loadStats();
  loadUsers();
};

const changeStatus = (value) => {
  statusFilter.value = value;
  refreshUsers();
};

const prevPage = () => {
  if (page.value <= 1) return;
  page.value--;
  loadUsers();
};

const nextPage = () => {
  if (page.value * pageSize >= total.value) return;
  page.value++;
  loadUsers();
};

const openEdit = (user) => {
  editTarget.value = user;
  editForm.value = {
    username: user.username,
    email: user.email,
    is_admin: user.is_admin,
    is_active: user.is_active
  };
  editing.value = true;
};

const closeEdit = () => {
  editing.value = false;
  editTarget.value = {};
};

const saveEdit = async () => {
  if (!editForm.value.username || editForm.value.username.length < 4) {
    return uni.showToast({ title: '用户名至少4位', icon: 'none' });
  }
  if (!editForm.value.email) {
    return uni.showToast({ title: '请输入邮箱', icon: 'none' });
  }
  saving.value = true;
  try {
    await http.updateAdminUser(editTarget.value.id, editForm.value);
    uni.showToast({ title: '保存成功', icon: 'success' });
    closeEdit();
    loadStats();
    loadUsers();
  } catch (error) {
    console.error('保存用户失败', error);
  } finally {
    saving.value = false;
  }
};

const openReset = (user) => {
  resetTarget.value = user;
  newPassword.value = '';
  resetting.value = true;
};

const closeReset = () => {
  resetting.value = false;
  resetTarget.value = {};
  newPassword.value = '';
};

const savePassword = async () => {
  if (!newPassword.value || newPassword.value.length < 4) {
    return uni.showToast({ title: '密码至少4位', icon: 'none' });
  }
  saving.value = true;
  try {
    await http.resetAdminUserPassword(resetTarget.value.id, newPassword.value);
    uni.showToast({ title: '密码已重置', icon: 'success' });
    closeReset();
  } catch (error) {
    console.error('重置密码失败', error);
  } finally {
    saving.value = false;
  }
};

const freezeUser = (user) => {
  uni.showModal({
    title: '确认冻结',
    content: `冻结后 ${user.username} 将无法登录`,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await http.freezeAdminUser(user.id);
        uni.showToast({ title: '已冻结', icon: 'success' });
        loadStats();
        loadUsers();
      } catch (error) {
        console.error('冻结失败', error);
      }
    }
  });
};

const unfreezeUser = async (user) => {
  try {
    await http.unfreezeAdminUser(user.id);
    uni.showToast({ title: '已解冻', icon: 'success' });
    loadStats();
    loadUsers();
  } catch (error) {
    console.error('解冻失败', error);
  }
};

const deleteUser = (user) => {
  uni.showModal({
    title: '确认删除',
    content: `确定删除用户 ${user.username} 吗？`,
    success: async (res) => {
      if (!res.confirm) return;
      try {
        await http.deleteAdminUser(user.id);
        uni.showToast({ title: '已删除', icon: 'success' });
        if (users.value.length === 1 && page.value > 1) {
          page.value--;
        }
        loadStats();
        loadUsers();
      } catch (error) {
        console.error('删除失败', error);
      }
    }
  });
};

onLoad(() => {
  if (ensureAdmin()) {
    loadStats();
    loadUsers();
  }
});

onPullDownRefresh(() => {
  refreshUsers();
});
</script>

<style scoped>
.page { min-height: 100vh; background: #f4f6f8; padding: 24rpx; box-sizing: border-box; }
.admin-topbar { display: flex; justify-content: space-between; align-items: center; background: #18202f; color: #fff; padding: 22rpx 24rpx; border-radius: 8rpx; margin-bottom: 20rpx; }
.admin-title { font-size: 32rpx; font-weight: bold; }
.admin-user { font-size: 24rpx; color: #c6d0df; margin-top: 6rpx; }
.logout-btn { margin: 0; color: #18202f; background: #fff; }
.logout-btn::after { border: none; }
.toolbar { display: flex; align-items: center; gap: 16rpx; margin-bottom: 20rpx; }
.search-input { flex: 1; background: #fff; border: 1px solid #d9e0e7; border-radius: 8rpx; padding: 18rpx 20rpx; font-size: 28rpx; box-sizing: border-box; }
.search-btn { background: #1677ff; color: #fff; margin: 0; }
.filters { display: flex; background: #fff; border: 1px solid #d9e0e7; border-radius: 8rpx; overflow: hidden; margin-bottom: 20rpx; }
.filter-item { flex: 1; text-align: center; padding: 18rpx 0; font-size: 26rpx; color: #4e5969; }
.filter-item.active { background: #e8f1ff; color: #1677ff; font-weight: bold; }
.summary { display: flex; justify-content: space-between; color: #6b7280; font-size: 24rpx; margin-bottom: 16rpx; }
.empty { text-align: center; color: #8a94a6; padding: 80rpx 0; font-size: 28rpx; }
.error-text { color: #c62828; }
.user-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8rpx; padding: 24rpx; margin-bottom: 18rpx; }
.user-main { display: flex; justify-content: space-between; align-items: flex-start; gap: 20rpx; }
.username { font-size: 32rpx; font-weight: bold; color: #1f2937; }
.email { color: #667085; font-size: 24rpx; margin-top: 8rpx; }
.badges { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8rpx; }
.badge { font-size: 22rpx; padding: 6rpx 12rpx; border-radius: 6rpx; }
.admin { background: #fff3d6; color: #9a6100; }
.active-badge { background: #e8f8ef; color: #16803c; }
.frozen-badge { background: #ffecec; color: #c62828; }
.actions { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 20rpx; }
.actions button { margin: 0; }
.primary-btn { background: #1677ff; color: #fff; }
.warn-btn { background: #faad14; color: #fff; }
.ok-btn { background: #22a06b; color: #fff; }
.danger-btn { background: #e5484d; color: #fff; }
.pager { display: flex; justify-content: center; gap: 24rpx; padding: 20rpx 0 40rpx; }
.modal-mask { position: fixed; left: 0; top: 0; right: 0; bottom: 0; z-index: 99; background: rgba(0, 0, 0, 0.45); display: flex; align-items: center; justify-content: center; padding: 32rpx; box-sizing: border-box; }
.modal { width: 100%; max-width: 680rpx; background: #fff; border-radius: 8rpx; padding: 30rpx; box-sizing: border-box; }
.modal-title { font-size: 34rpx; font-weight: bold; color: #111827; margin-bottom: 24rpx; }
.modal-input { border: 1px solid #d9e0e7; border-radius: 8rpx; padding: 18rpx 20rpx; margin-bottom: 20rpx; font-size: 28rpx; }
.switch-row { display: flex; justify-content: space-between; align-items: center; padding: 16rpx 0; font-size: 28rpx; color: #374151; }
.target-user { color: #667085; font-size: 24rpx; margin-bottom: 20rpx; }
.modal-actions { display: flex; justify-content: flex-end; gap: 16rpx; margin-top: 24rpx; }
.modal-actions button { margin: 0; }
</style>
