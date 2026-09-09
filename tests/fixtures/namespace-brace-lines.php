<?php
namespace
/* The opening token is not this comment's { or its
 * closing brace }. */
{
    use function Target\f as Self;
}
namespace Named
{
    use const Target\C as Parent;
}
namespace
// The actual brace follows this comment.
{
    use Target\ClassName;
}
