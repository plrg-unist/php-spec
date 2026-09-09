<?php declare(strict_types=1);

namespace PhpParser\Node\Stmt;

use PhpParser\Node;

class Foreach_ extends Node\Stmt {
    /** @var Node\Expr Expression to iterate */
    public Node\Expr $expr;
    /** @var null|Node\Expr Variable to assign key to */
    public ?Node\Expr $keyVar;
    /** @var bool Whether to assign value by reference */
    public bool $byRef;
    /** @var Node\Expr Variable to assign value to */
    public Node\Expr $valueVar;
    /** @var Node\Stmt[] Statements */
    public array $stmts;
    /** @var bool Whether to assign key by reference (rejected during compilation) */
    public bool $keyByRef;

    /**
     * Constructs a foreach node.
     *
     * @param Node\Expr $expr Expression to iterate
     * @param Node\Expr $valueVar Variable to assign value to
     * @param array{
     *     keyVar?: Node\Expr|null,
     *     byRef?: bool,
     *     stmts?: Node\Stmt[],
     *     keyByRef?: bool,
     * } $subNodes Array of the following optional subnodes:
     *             'keyVar' => null   : Variable to assign key to
     *             'byRef'  => false  : Whether to assign value by reference
     *             'stmts'  => array(): Statements
     *             'keyByRef' => false: Whether to assign key by reference
     * @param array<string, mixed> $attributes Additional attributes
     */
    public function __construct(Node\Expr $expr, Node\Expr $valueVar, array $subNodes = [], array $attributes = []) {
        $this->attributes = $attributes;
        $this->expr = $expr;
        $this->keyVar = $subNodes['keyVar'] ?? null;
        $this->byRef = $subNodes['byRef'] ?? false;
        $this->valueVar = $valueVar;
        $this->stmts = $subNodes['stmts'] ?? [];
        $this->keyByRef = $subNodes['keyByRef'] ?? false;
    }

    public function getSubNodeNames(): array {
        return ['expr', 'keyVar', 'byRef', 'valueVar', 'stmts', 'keyByRef'];
    }

    public function getType(): string {
        return 'Stmt_Foreach';
    }
}
