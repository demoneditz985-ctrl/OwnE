.class public final Lcom/shadowmodz/KeyAction;
.super Ljava/lang/Object;
.implements Landroid/view/View$OnClickListener;

.field private final activity:Lcom/shadowmodz/KeyActivity;
.field private final action:I

.method public constructor <init>(Lcom/shadowmodz/KeyActivity;I)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/shadowmodz/KeyAction;->activity:Lcom/shadowmodz/KeyActivity;
    iput p2, p0, Lcom/shadowmodz/KeyAction;->action:I
    return-void
.end method

.method public onClick(Landroid/view/View;)V
    .locals 2
    iget-object v0, p0, Lcom/shadowmodz/KeyAction;->activity:Lcom/shadowmodz/KeyActivity;
    iget v1, p0, Lcom/shadowmodz/KeyAction;->action:I
    if-nez v1, :telegram
    invoke-virtual {v0}, Lcom/shadowmodz/KeyActivity;->attempt()V
    return-void
    :telegram
    invoke-virtual {v0}, Lcom/shadowmodz/KeyActivity;->telegram()V
    return-void
.end method
