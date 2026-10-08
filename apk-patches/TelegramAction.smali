.class public final Lcom/shadowmodz/TelegramAction;
.super Ljava/lang/Object;
.implements Landroidx/emoji2/text/wm0;

.field private final context:Landroid/content/Context;

.method public constructor <init>(Landroid/content/Context;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/shadowmodz/TelegramAction;->context:Landroid/content/Context;
    return-void
.end method

# The existing activation dialog's secondary CTA opens the owner's invite.
# This does NOT activate a licence or replace the native licence checks.
.method public final a()Ljava/lang/Object;
    .locals 4

    iget-object v0, p0, Lcom/shadowmodz/TelegramAction;->context:Landroid/content/Context;
    new-instance v1, Landroid/content/Intent;
    const-string v2, "android.intent.action.VIEW"
    const-string v3, "https://t.me/+BBimnHMiSvpiYTBl"
    invoke-static {v3}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;
    move-result-object v3
    invoke-direct {v1, v2, v3}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V
    const/high16 v2, 0x10000000
    invoke-virtual {v1, v2}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    :try_start
    invoke-virtual {v0, v1}, Landroid/content/Context;->startActivity(Landroid/content/Intent;)V
    :try_end
    .catch Landroid/content/ActivityNotFoundException; {:try_start .. :try_end} :unavailable
    .catch Ljava/lang/SecurityException; {:try_start .. :try_end} :unavailable

    :done
    sget-object v0, Landroidx/emoji2/text/jq2;->a:Landroidx/emoji2/text/jq2;
    return-object v0

    :unavailable
    move-exception v1
    const-string v1, "Open t.me/+BBimnHMiSvpiYTBl in your browser to join Shadow Modz."
    const/4 v2, 0x1
    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    move-result-object v0
    invoke-virtual {v0}, Landroid/widget/Toast;->show()V
    goto :done
.end method
