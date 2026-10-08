.class public final Lcom/shadowmodz/KeyActivity;
.super Landroid/app/Activity;

.field private input:Landroid/widget/EditText;
.field private error:Landroid/widget/TextView;

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method private find(Ljava/lang/String;)Landroid/view/View;
    .locals 3
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v0
    const-string v1, "id"
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;
    move-result-object v2
    invoke-virtual {v0, p1, v1, v2}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I
    move-result v0
    invoke-virtual {p0, v0}, Landroid/app/Activity;->findViewById(I)Landroid/view/View;
    move-result-object v0
    return-object v0
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 4
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->remember(Landroid/content/Context;)V
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->isAccepted(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :show_form
    invoke-virtual {p0}, Lcom/shadowmodz/KeyActivity;->openMain()V
    return-void
    :show_form
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v0
    const-string v1, "shadow_key_gate"
    const-string v2, "layout"
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;
    move-result-object v3
    invoke-virtual {v0, v1, v2, v3}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I
    move-result v0
    invoke-virtual {p0, v0}, Landroid/app/Activity;->setContentView(I)V
    const-string v0, "shadow_key_input"
    invoke-direct {p0, v0}, Lcom/shadowmodz/KeyActivity;->find(Ljava/lang/String;)Landroid/view/View;
    move-result-object v0
    check-cast v0, Landroid/widget/EditText;
    iput-object v0, p0, Lcom/shadowmodz/KeyActivity;->input:Landroid/widget/EditText;
    const-string v0, "shadow_key_error"
    invoke-direct {p0, v0}, Lcom/shadowmodz/KeyActivity;->find(Ljava/lang/String;)Landroid/view/View;
    move-result-object v0
    check-cast v0, Landroid/widget/TextView;
    iput-object v0, p0, Lcom/shadowmodz/KeyActivity;->error:Landroid/widget/TextView;
    const-string v0, "shadow_key_continue"
    invoke-direct {p0, v0}, Lcom/shadowmodz/KeyActivity;->find(Ljava/lang/String;)Landroid/view/View;
    move-result-object v0
    new-instance v1, Lcom/shadowmodz/KeyAction;
    const/4 v2, 0x0
    invoke-direct {v1, p0, v2}, Lcom/shadowmodz/KeyAction;-><init>(Lcom/shadowmodz/KeyActivity;I)V
    invoke-virtual {v0, v1}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V
    const-string v0, "shadow_key_telegram"
    invoke-direct {p0, v0}, Lcom/shadowmodz/KeyActivity;->find(Ljava/lang/String;)Landroid/view/View;
    move-result-object v0
    new-instance v1, Lcom/shadowmodz/KeyAction;
    const/4 v2, 0x1
    invoke-direct {v1, p0, v2}, Lcom/shadowmodz/KeyAction;-><init>(Lcom/shadowmodz/KeyActivity;I)V
    invoke-virtual {v0, v1}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V
    return-void
.end method

.method public attempt()V
    .locals 2
    iget-object v0, p0, Lcom/shadowmodz/KeyActivity;->input:Landroid/widget/EditText;
    invoke-virtual {v0}, Landroid/widget/EditText;->getText()Landroid/text/Editable;
    move-result-object v0
    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lcom/shadowmodz/KeyPolicy;->matches(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :wrong_key
    invoke-static {p0, v0}, Lcom/shadowmodz/KeyPolicy;->save(Landroid/content/Context;Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :save_failed
    invoke-virtual {p0}, Lcom/shadowmodz/KeyActivity;->openMain()V
    return-void
    :wrong_key
    const-string v0, "Invalid Shadow Modz key."
    goto :show_error
    :save_failed
    const-string v0, "Could not save the local key. Please retry."
    :show_error
    iget-object v1, p0, Lcom/shadowmodz/KeyActivity;->error:Landroid/widget/TextView;
    invoke-virtual {v1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V
    return-void
.end method

.method public openMain()V
    .locals 3
    # Refuse a direct call unless a validated, saved local proof exists.
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->isAccepted(Landroid/content/Context;)Z
    move-result v0
    if-eqz v0, :done
    :try_start
    new-instance v0, Landroid/content/Intent;
    invoke-direct {v0}, Landroid/content/Intent;-><init>()V
    const-string v1, "com.kos"
    const-string v2, "com.kos.MainActivity"
    invoke-virtual {v0, v1, v2}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;
    invoke-virtual {p0, v0}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V
    invoke-virtual {p0}, Landroid/app/Activity;->finish()V
    :try_end
    .catch Ljava/lang/RuntimeException; {:try_start .. :try_end} :failed
    :done
    return-void
    :failed
    move-exception v0
    const-string v0, "The original app could not start. Native engine licensing is unchanged."
    const/4 v1, 0x1
    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v0
    invoke-virtual {v0}, Landroid/widget/Toast;->show()V
    return-void
.end method

.method public telegram()V
    .locals 3
    :try_start
    const-string v0, "https://t.me/+BBimnHMiSvpiYTBl"
    invoke-static {v0}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;
    move-result-object v0
    new-instance v1, Landroid/content/Intent;
    const-string v2, "android.intent.action.VIEW"
    invoke-direct {v1, v2, v0}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V
    invoke-virtual {p0, v1}, Landroid/app/Activity;->startActivity(Landroid/content/Intent;)V
    :try_end
    .catch Landroid/content/ActivityNotFoundException; {:try_start .. :try_end} :no_browser
    return-void
    :no_browser
    move-exception v0
    const-string v0, "Install Telegram or a browser to open the invite."
    const/4 v1, 0x0
    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v0
    invoke-virtual {v0}, Landroid/widget/Toast;->show()V
    return-void
.end method
