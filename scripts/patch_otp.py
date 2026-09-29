import re

with open('D:/IDEATHON/frontend/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update setAuthMode to NOT show OTP initially
old_otp_reset = '''  // Reset OTP step
  if (loginOtp) {
    isOtpStep = true;
    if (byId("group-otp")) byId("group-otp").hidden = false;
    if (byId("auth-otp")) byId("auth-otp").required = true;
  } else {
    isOtpStep = false;
    if (byId("group-otp")) byId("group-otp").hidden = true;
    if (byId("auth-otp")) byId("auth-otp").required = false;
  }'''

new_otp_reset = '''  // Reset OTP step
  isOtpStep = false;
  if (byId("group-otp")) byId("group-otp").hidden = true;
  if (byId("auth-otp")) {
    byId("auth-otp").required = false;
    byId("auth-otp").value = "";
  }
  
  if (loginOtp && btnTextNode) {
    btnTextNode.textContent = "Get OTP";
  }
'''
code = code.replace(old_otp_reset, new_otp_reset)

# 2. Update auth form submit logic to handle isOtpStep properly
old_submit_success = '''    if (result.status === "otp_sent") {
      isOtpStep = true;
      byId("auth-message").textContent =
        "OTP sent to your email. Please verify.";

      if (forgot) {
        byId("group-password").hidden = false;
        byId("auth-password").required = true;
        if (byId("password-rules")) byId("password-rules").hidden = false;
      } else {
        byId("group-password").hidden = true;
        byId("auth-password").required = false;
        if (byId("password-rules")) byId("password-rules").hidden = true;
      }

      byId("group-otp").hidden = false;
      byId("auth-otp").required = true;

      let btnText = "Verify OTP";
      if (forgot) btnText = "Reset Password";
      else if (loginOtp) btnText = "Login";
      
      if (byId("auth-submit-btn"))
        byId("auth-submit-btn").textContent = btnText;
      return;
    }'''

new_submit_success = '''    if (result.status === "otp_sent") {
      isOtpStep = true;
      byId("auth-message").textContent = "OTP sent to your email. Please verify.";
      byId("auth-message").style.color = "var(--primary-color)";

      if (forgot) {
        if (byId("group-password")) {
          byId("group-password").hidden = false;
          byId("auth-password").required = true;
        }
        if (byId("password-rules")) byId("password-rules").hidden = false;
      }

      if (byId("group-otp")) byId("group-otp").hidden = false;
      if (byId("auth-otp")) byId("auth-otp").required = true;

      let btnText = "Verify OTP";
      if (forgot) btnText = "Reset Password";
      else if (loginOtp) btnText = "Login";
      
      if (byId("auth-btn-text"))
        byId("auth-btn-text").textContent = btnText;
      return;
    }'''
code = code.replace(old_submit_success, new_submit_success)

# 3. Prevent form submit from failing if auth-password is null
# Since we removed password link, we don't care, but just in case
code = code.replace('payload.password = byId("auth-password").value;', 'payload.password = byId("auth-password") ? byId("auth-password").value : "";')

with open('D:/IDEATHON/frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(code)
