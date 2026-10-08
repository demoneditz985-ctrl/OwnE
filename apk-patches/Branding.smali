.class public final Lcom/shadowmodz/Branding;
.super Ljava/lang/Object;

# This helper is called only at the Compose Text rendering boundary.
# Do not call it from native string decoding, protocol, or filesystem code.
.method public static displayText(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    if-eqz p0, :done

    const-string v0, "KOS"
    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v0
    if-eqz v0, :done

    const-string v0, "\\bKOS\\b"
    const-string v1, "Shadow Modz"
    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object p0

    :done
    return-object p0
.end method
