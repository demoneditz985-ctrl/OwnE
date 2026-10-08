.class public final Lcom/shadowmodz/KeyPolicy;
.super Ljava/lang/Object;

# A local entry lock only. Not a native-engine entitlement or server token.
.field private static volatile context:Landroid/content/Context;

.method public static remember(Landroid/content/Context;)V
    .locals 1
    if-eqz p0, :store
    :try_start
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;
    move-result-object v0
    if-eqz v0, :store
    move-object p0, v0
    :try_end
    .catch Ljava/lang/RuntimeException; {:try_start .. :try_end} :not_attached
    goto :store
    :not_attached
    move-exception v0
    # Factory application creation precedes Context attachment. Keep only the
    # supplied Application reference until Android has attached it.
    :store
    sput-object p0, Lcom/shadowmodz/KeyPolicy;->context:Landroid/content/Context;
    return-void
.end method

.method public static matches(Ljava/lang/String;)Z
    .locals 1
    if-eqz p0, :reject
    invoke-virtual {p0}, Ljava/lang/String;->trim()Ljava/lang/String;
    move-result-object p0
    const-string v0, "SHADOWMODZ"
    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    return v0
    :reject
    const/4 v0, 0x0
    return v0
.end method

.method private static preferences(Landroid/content/Context;)Landroid/content/SharedPreferences;
    .locals 2
    const-string v0, "shadow_modz_local_gate"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0
    return-object v0
.end method

.method public static isAccepted(Landroid/content/Context;)Z
    .locals 3
    if-eqz p0, :reject
    :try_start
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->preferences(Landroid/content/Context;)Landroid/content/SharedPreferences;
    move-result-object v0
    const-string v1, "proof"
    const-string v2, ""
    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    const-string v1, "shadow-local-key-v1:SHADOWMODZ"
    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    :try_end
    .catch Ljava/lang/RuntimeException; {:try_start .. :try_end} :error
    return v0
    :error
    move-exception v0
    :reject
    const/4 v0, 0x0
    return v0
.end method

.method public static isAccepted()Z
    .locals 1
    sget-object v0, Lcom/shadowmodz/KeyPolicy;->context:Landroid/content/Context;
    invoke-static {v0}, Lcom/shadowmodz/KeyPolicy;->isAccepted(Landroid/content/Context;)Z
    move-result v0
    return v0
.end method

.method public static save(Landroid/content/Context;Ljava/lang/String;)Z
    .locals 3
    invoke-static {p1}, Lcom/shadowmodz/KeyPolicy;->matches(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :reject
    if-eqz p0, :reject
    :try_start
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->preferences(Landroid/content/Context;)Landroid/content/SharedPreferences;
    move-result-object v0
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    const-string v1, "proof"
    const-string v2, "shadow-local-key-v1:SHADOWMODZ"
    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->commit()Z
    move-result v1
    if-eqz v1, :rollback
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->remember(Landroid/content/Context;)V
    invoke-static {p0}, Lcom/shadowmodz/KeyPolicy;->isAccepted(Landroid/content/Context;)Z
    move-result v1
    :try_end
    .catch Ljava/lang/RuntimeException; {:try_start .. :try_end} :error
    return v1
    :rollback
    const-string v1, "proof"
    invoke-interface {v0, v1}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;
    # Reset the in-memory proof even if the filesystem write failed.
    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V
    goto :reject
    :error
    move-exception v0
    :reject
    const/4 v0, 0x0
    return v0
.end method
