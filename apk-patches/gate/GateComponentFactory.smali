.class public final Lcom/shadowmodz/GateComponentFactory;
.super Landroidx/emoji2/text/g20;

.method public constructor <init>()V
    .locals 1
    invoke-direct {p0}, Landroidx/emoji2/text/g20;-><init>()V
    # Retain the old factory's library-loading behavior. This does not fix a
    # native startup/signature rejection that happens before the key screen.
    const-string v0, "kos"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    return-void
.end method

.method public instantiateApplication(Ljava/lang/ClassLoader;Ljava/lang/String;)Landroid/app/Application;
    .locals 1
    invoke-super {p0, p1, p2}, Landroidx/emoji2/text/g20;->instantiateApplication(Ljava/lang/ClassLoader;Ljava/lang/String;)Landroid/app/Application;
    move-result-object v0
    # Save the reference only. Android attaches its Context after this method;
    # preferences are not read until activity instantiation after attachment.
    invoke-static {v0}, Lcom/shadowmodz/KeyPolicy;->remember(Landroid/content/Context;)V
    return-object v0
.end method

.method public instantiateActivity(Ljava/lang/ClassLoader;Ljava/lang/String;Landroid/content/Intent;)Landroid/app/Activity;
    .locals 2
    const-string v0, "com.kos.MainActivity"
    invoke-virtual {v0, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :create
    invoke-static {}, Lcom/shadowmodz/KeyPolicy;->isAccepted()Z
    move-result v0
    if-nez v0, :create
    const-string p2, "com.shadowmodz.KeyActivity"
    :create
    invoke-super {p0, p1, p2, p3}, Landroidx/emoji2/text/g20;->instantiateActivity(Ljava/lang/ClassLoader;Ljava/lang/String;Landroid/content/Intent;)Landroid/app/Activity;
    move-result-object v0
    return-object v0
.end method
