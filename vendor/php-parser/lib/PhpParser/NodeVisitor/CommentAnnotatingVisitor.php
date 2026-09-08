<?php declare(strict_types=1);

namespace PhpParser\NodeVisitor;

use PhpParser\Comment;
use PhpParser\Node;
use PhpParser\NodeVisitorAbstract;
use PhpParser\Token;

class CommentAnnotatingVisitor extends NodeVisitorAbstract {
    /** @var int Last seen token start position */
    private int $pos = 0;
    /** @var Token[] Token array */
    private array $tokens;
    /** @var list<int> Token positions of comments */
    private array $commentPositions = [];

    /**
     * Create a comment annotation visitor.
     *
     * @param Token[] $tokens Token array
     */
    public function __construct(array $tokens) {
        $this->tokens = $tokens;

        // Collect positions of comments. We use this to avoid traversing parts of the AST where
        // there are no comments.
        foreach ($tokens as $i => $token) {
            if ($token->id === \T_COMMENT || $token->id === \T_DOC_COMMENT) {
                $this->commentPositions[] = $i;
            }
        }
    }

    public function enterNode(Node $node) {
        $nextCommentPos = current($this->commentPositions);
        if ($nextCommentPos === false) {
            // No more comments.
            return self::STOP_TRAVERSAL;
        }

        $oldPos = $this->pos;
        $this->pos = $pos = $node->getStartTokenPos();
        if ($nextCommentPos > $oldPos && $nextCommentPos < $pos) {
            $comments = [];
            while (--$pos >= $oldPos) {
                $token = $this->tokens[$pos];
                if ($token->id === \T_DOC_COMMENT) {
                    $comments[] = new Comment\Doc(
                        $token->text, $token->line, $token->pos, $pos,
                        $token->getEndLine(), $token->getEndPos() - 1, $pos);
                    continue;
                }
                if ($token->id === \T_COMMENT) {
                    $comments[] = new Comment(
                        $token->text, $token->line, $token->pos, $pos,
                        $token->getEndLine(), $token->getEndPos() - 1, $pos);
                    continue;
                }
                if ($token->id !== \T_WHITESPACE) {
                    break;
                }
            }
            if (!empty($comments)) {
                $node->setAttribute('comments', array_reverse($comments));
            }

            do {
                $nextCommentPos = next($this->commentPositions);
            } while ($nextCommentPos !== false && $nextCommentPos < $this->pos);
        }

        $endPos = $node->getEndTokenPos();
        if ($nextCommentPos > $endPos) {
            // Skip children if there are no comments located inside this node.
            $this->pos = $endPos;
            return self::DONT_TRAVERSE_CHILDREN;
        }

        return null;
    }
    public function afterTraverse(array $nodes) {
        // Parentheses, operators and punctuation may have no surviving AST node.
        // Preserve their comments on the nearest containing node, promoted to the
        // outermost node with the same start. Existing declaration annotations
        // stay in place; this pass only recovers comments the visitor did not use.
        $assigned = [];
        $starts = [];
        $pending = $nodes;
        while ($pending) {
            $node = array_pop($pending);
            foreach ($node->getComments() as $comment) {
                $assigned[$comment->getStartTokenPos()] = true;
            }
            $start = $node->getStartTokenPos();
            $end = $node->getEndTokenPos();
            if ($start <= $end && (!isset($starts[$start]) || $end > $starts[$start][1])) {
                $starts[$start] = [$node, $end];
            }
            foreach ($node->getSubNodeNames() as $name) {
                $child = $node->$name;
                if ($child instanceof Node) {
                    $pending[] = $child;
                } elseif (is_array($child)) {
                    foreach ($child as $item) {
                        if ($item instanceof Node) $pending[] = $item;
                    }
                }
            }
        }
        ksort($starts);
        $positions = array_keys($starts);
        $active = [];
        $next = 0;
        foreach ($this->commentPositions as $pos) {
            if (isset($assigned[$pos])) continue;
            while ($next < count($positions) && $positions[$next] <= $pos) {
                $start = $positions[$next++];
                while ($active && $active[count($active) - 1][1] < $start) array_pop($active);
                $active[] = $starts[$start];
            }
            while ($active && $active[count($active) - 1][1] < $pos) array_pop($active);
            $owner = $active ? $active[count($active) - 1][0]
                : ($next < count($positions) ? $starts[$positions[$next]][0] : null);
            if ($owner === null) {
                throw new \LogicException('Comment has no syntax attachment');
            }
            $token = $this->tokens[$pos];
            $class = $token->id === \T_DOC_COMMENT ? Comment\Doc::class : Comment::class;
            $comment = new $class($token->text, $token->line, $token->pos, $pos,
                $token->getEndLine(), $token->getEndPos() - 1, $pos);
            $comments = $owner->getComments();
            $comments[] = $comment;
            usort($comments, static fn(Comment $a, Comment $b): int =>
                $a->getStartTokenPos() <=> $b->getStartTokenPos());
            $owner->setAttribute('comments', $comments);
        }
        return null;
    }

}
