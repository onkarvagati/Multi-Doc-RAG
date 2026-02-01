css = """
<style>
.chat-container {
    max-width: 850px;
    margin: auto;
    padding-top: 10px;
}

.chat-message {
    display: flex;
    gap: 12px;
    margin-bottom: 14px;
    align-items: flex-start;
}

.chat-message.user {
    flex-direction: row-reverse;
}

.chat-message .avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
}

.chat-message .message {
    padding: 14px 18px;
    border-radius: 14px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.6;
}

.chat-message.user .message {
    background-color: #2563eb;
    color: white;
    border-top-right-radius: 4px;
}

.chat-message.bot .message {
    background-color: #f3f4f6;
    color: #111827;
    border-top-left-radius: 4px;
}

.sources {
    font-size: 12px;
    color: #6b7280;
    margin-top: 6px;
}
</style>
"""

user_template = """
<div class="chat-message user">
    <img class="avatar" src="https://cdn-icons-png.flaticon.com/512/847/847969.png">
    <div class="message">{{MSG}}</div>
</div>
"""

bot_template = """
<div class="chat-message bot">
    <img class="avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png">
    <div class="message">{{MSG}}</div>
</div>
"""