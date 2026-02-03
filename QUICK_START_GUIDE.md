# Quick Start Guide - New Features

## 🚀 Getting Started with New Features

### For End Users

#### 1. View Dashboard with Real-time Updates
```
1. Log in to your account
2. Dashboard automatically loads
3. See your rank, points, and active tournaments
4. Watch stats update in real-time (no refresh needed!)
```

#### 2. Check Notifications
```
1. Look for bell icon in top-right
2. Red badge shows unread count
3. Click bell to see latest notifications
4. Click notification to mark as read
```

#### 3. Edit Your Profile
```
1. Click "My Profile" in sidebar
2. Update your name, bio, phone, avatar
3. See avatar preview as you type URL
4. Click "Save Changes"
```

#### 4. Read Blog Posts
```
1. Click "Blog" in sidebar
2. Browse health and fitness tips
3. Click any post to read full article
4. Latest 3 posts also shown on dashboard
```

#### 5. Reset Your Password
```
1. On login page, click "Forgot Password"
2. Enter your email
3. Check email for reset token
4. Use token on password reset page
5. Enter new password (twice)
6. Log in with new password
```

---

### For Admins/Trainers

#### 1. Create Blog Posts
```
1. Go to Admin Panel
2. Click "Blog Management" tab
3. Click "Create New Post"
4. Fill in title, content, image URL
5. Check "Published" to make it live
6. Click "Create Post"
```

#### 2. Send Notifications
```
1. Go to Admin Panel
2. Navigate to notification section
3. Select user or broadcast to all
4. Write title and message
5. Choose type (info/success/warning/error)
6. Send notification
```

---

## 📋 Quick Reference

### New Pages
- `/dashboard.html` - Enhanced with real-time updates
- `/profile.html` - Edit your profile
- `/blog.html` - Browse blog posts
- `/blog-post.html?slug=...` - Read individual post
- `/forgot-password.html` - Request password reset
- `/password-reset.html` - Reset password with token

### New Features
- 🔔 Live notifications with bell icon
- 📝 Blog system for content
- ⚡ Real-time dashboard updates
- 👤 Profile management
- 🔑 Password reset flow

### WebSocket Events (Real-time)
- Leaderboard updates
- New notifications
- Tournament updates
- Scoring changes

---

## 🛠️ For Developers

### Run Database Migrations
```bash
cd services/user-service
flask db migrate -m "Add notifications, blog, reset tokens"
flask db upgrade
```

### Restart Services
```bash
docker-compose restart user-service
docker-compose restart notification-service
docker-compose restart api-gateway
```

### Test API Endpoints
```bash
# Get notifications
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/notifications

# Get blog posts
curl http://localhost:8000/api/users/blog/posts

# Update profile
curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"full_name":"New Name"}' http://localhost:8000/api/users/me
```

---

## ✅ Feature Checklist

**Can you:**
- [ ] See real-time stats on dashboard?
- [ ] Click bell to see notifications?
- [ ] Mark notifications as read?
- [ ] Edit your profile?
- [ ] See avatar preview update?
- [ ] Read blog posts?
- [ ] Request password reset?
- [ ] Reset password with token?

**If any checkbox is unchecked, refer to FEATURES_IMPLEMENTED.md for detailed troubleshooting.**

---

## 🆘 Troubleshooting

### Dashboard not updating in real-time?
- Check browser console for WebSocket errors
- Ensure notification-service is running
- Verify Redis is accessible

### Notifications not showing?
- Check if you're logged in
- Verify JWT token is valid
- Check API endpoint: `/api/users/notifications`

### Blog posts not loading?
- Check if any posts are published
- Verify user-service is running
- Test API: `/api/users/blog/posts`

### Profile changes not saving?
- Check network tab for errors
- Verify JWT token in request
- Check API endpoint: `/api/users/me`

### Password reset not working?
- Check token hasn't expired (1 hour)
- Verify token hasn't been used already
- Try requesting new token

---

## 📚 Additional Resources

- **Full Documentation:** See `FEATURES_IMPLEMENTED.md`
- **API Reference:** Check code comments in `api.py`
- **Database Schema:** See `models.py`
- **Frontend Code:** Browse `/static/js/` directory

---

## 🎉 Enjoy the New Features!

All features are production-ready and tested. If you encounter any issues, please check the documentation or contact support.

**Happy using the enhanced GYM-IT System!** 💪
